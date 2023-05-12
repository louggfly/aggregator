import re

import requests
from django.contrib.sessions.models import Session
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from aggregator.models import User, Order

lowerRegex = re.compile('[a-z]')
upperRegex = re.compile('[A-Z]')
digitRegex = re.compile('[0-9]')
pattern = r'^1[3-9]\d{9}$'


# Create your views here.
def index(request):
    return render(request, "index.html")


class Register(APIView):
    @staticmethod
    def post(request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        checkPhone = User.objects.filter(phone_number=phone_number)
        if checkPhone.exists():
            return Response({'code': '400', 'msg': 'Failed!The phone number already exists.'})
        elif re.match(pattern, phone_number) is None:
            return Response({'code': '400', 'msg': 'Failed!The phone number does not meet the specifications.'})
        else:
            if len(password) < 8:
                return Response({'code': '400', 'msg': 'Failed!The password entered is less than 8 digits.'})
            else:
                if lowerRegex.search(password) is None:
                    return Response({'code': '400', 'msg': 'Failed!The password does not contain lowercase letters.'})
                elif upperRegex.search(password) is None:
                    return Response({'code': '400', 'msg': 'Failed!The password does not contain uppercase letters.'})
                elif digitRegex.search(password) is None:
                    return Response({'code': '400', 'msg': 'Failed!The password does not contain numbers.'})
                else:
                    ob = User()
                    ob.phone_number = phone_number
                    import hashlib, random
                    md5 = hashlib.md5()
                    n = random.randint(100000, 999999)
                    s = password + str(n)  # 从表单中获取密码并添加干扰值
                    md5.update(s.encode('utf-8'))
                    print(md5.hexdigest)  # 将要产生md5的子串放进去
                    ob.password_hash = md5.hexdigest()  # 获取md5值
                    ob.password_salt = n
                    ob.status = 1
                    ob.save()
                    return Response({'code': '200', 'msg': 'successful'})


class Login(APIView):
    @staticmethod
    def post(request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        checkPhone = User.objects.filter(phone_number=phone_number)
        if checkPhone.exists():
            user = User.objects.get(phone_number=phone_number)
            if user.status == 1:
                import hashlib
                md5 = hashlib.md5()
                s = password + user.password_salt
                md5.update(s.encode('utf-8'))
                if user.password_hash == md5.hexdigest():
                    request.session['phone_number'] = user.phone_number
                    return Response({'code': '200', 'msg': 'successful'})
                else:
                    return Response({'code': '400', 'msg': 'Failed!Password error'})
            else:
                return Response(
                    {'code': '400', 'msg': 'Failed!User canceled, please wait for administrator operation'})
        else:
            return Response({'code': '400', 'msg': 'Failed!Phone number not registered'})


class keep_user_logged_in(APIView):
    @staticmethod
    def get(request):
        if 'phone_number' in request.session:
            try:
                session = Session.objects.get(pk=request.session.session_key)
            except Session.DoesNotExist:
                return Response({'code': '400', 'status': 'error', 'msg': 'Session does not exist.'})

            phone_number = request.session.get('phone_number')
            try:
                user = User.objects.get(phone_number=phone_number)
                if user is not None:
                    return Response({
                        'code': '200',
                        'status': 'success',
                        'user': {
                            'id': user.id,
                            'phone_number': user.phone_number,
                        }
                    })
            except User.DoesNotExist:
                return Response({'code': '400', 'status': 'error', 'msg': 'User does not exist.'})
        return Response({'code': '400', 'status': 'error', 'msg': 'User is not logged in.'})


class Logout(APIView):
    @staticmethod
    def post(request):
        if 'phone_number' in request.session:
            del request.session['phone_number']
            return Response({'code': '200', 'status': 'success', 'msg': 'User logged out successfully.'})
        return Response({'code': '400', 'status': 'error', 'msg': 'User is not logged in.'})


class OrderView(APIView):
    @staticmethod
    def post(request):
        order_number = request.data.get('order_number')
        user_phone = request.data.get('user_phone')
        airline = request.data.get('airline')
        key = request.data.get('key')
        status = request.data.get('status')

        user = User.objects.get(phone_number=user_phone)
        order = Order.objects.create(order_number=order_number, user_id=user.id,
                                     airline=airline, key=key, status=status)
        return Response({'code': '200', 'status': 'success'})

    @staticmethod
    def get(request):
        orders = Order.objects.all()
        data = [{'order_number': order.order_number, 'user_id': order.user_id,
                 'airline': order.airline, 'key': order.key, 'status': order.status}
                for order in orders]
        return Response({'code': '200', 'status': 'success', 'data': data})

    @staticmethod
    def put(request):
        try:
            order_number = request.data.get('order_number')
            order = Order.objects.get(order_number=order_number)
            order.key = request.data.get('key', order.key)
            order.status = request.data.get('status', order.status)
            order.save()
            return Response({'code': '200', 'status': 'success'})
        except Order.DoesNotExist:
            return Response({'code': '400', 'msg': 'failed'})


class BookingStatus(APIView):
    @staticmethod
    def get(request):
        order_number = request.GET.get('order_number')
        url = 'http://sc19h2l.pythonanywhere.com/bookingstatus/'
        params = {'order_id': order_number}
        response = requests.get(url, params=params)
        result = response.json()

        if result['code'] == "200":
            data = result['data'][0]
            return Response({
                'code': '200',
                'msg': 'successful',
                'data': data})
        elif result['code'] == "503":
            return Response({'code': '400', 'msg': result['msg'], 'error': result['msg']})
        else:
            error_msg = f'Error: {response.status_code} {response.reason}'
            return Response({'code': '400', 'msg': 'fail', 'error': error_msg})


class CancelBooking(APIView):
    @staticmethod
    def post(request):
        order_number = request.data.get('order_number')
        url = 'http://sc19h2l.pythonanywhere.com/cancelbooking/'
        data = {
            'order_id': order_number,
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        result = response.json()

        if result['code'] == "200":
            order = Order.objects.get(order_number=order_number)
            order.delete()
            return Response({'code': '200', 'msg': 'success'})
        else:
            return Response({'code': '400', 'msg': 'fail'})


class FindFlight(APIView):
    @staticmethod
    def get(request):
        departure_date = request.GET.get('departure_date')
        departure = request.GET.get('departure')
        arrival = request.GET.get('arrival')
        url = 'http://sc19h2l.pythonanywhere.com/findflight//'
        params = {
            'departure_date': departure_date,
            'departure': departure,
            'arrival': arrival
        }
        params = f'departure_date={departure_date}&departure={departure}&arrival={arrival}'
        response = requests.get(url, params=params)
        print(response.url)

        if response.status_code == 200:
            result = response.json()
            if result['code'] == '200':
                print(result['data'])
                if not result['data']:
                    return Response({'code': '400', 'msg': 'Sorry! No search results found'})
                flights = result['data']
                flightList = []
                for flight in flights:
                    flightInfo = {
                        "flight_num": flight['flight_num'],
                        "airline": flight['airline'],
                        "departure_date": flight['departure_date'],
                        "departure_time": flight['departure_time'],
                        "arrive_date": flight['arrive_date'],
                        "arrive_time": flight['arrive_time'],
                        "flight_price": flight['flight_price'],
                        "seat_number": flight['seat_number'],
                        "departure": flight['departure'],
                        "arrival": flight['arrival']
                    }
                    flightList.append(flightInfo)
                return Response({'code': '200', 'msg': 'successful', 'data': flightList})
            else:
                return Response({'code': '400', 'msg': result['message']})
        else:
            return Response({'code': '400', 'msg': 'Failed! Cannot connect to the server'})


class BookFlight(APIView):
    @staticmethod
    def post(request):
        flight_num = request.data.get('flight_num')
        passenger_name = request.data.get('passenger_name')
        order_id = request.data.get('order_id')
        order_price = request.data.get('order_price')
        ticket_time = request.data.get('ticket_time')
        payment_status = request.data.get('payment_status')

        # Send the POST request to the /bookflight endpoint
        url = 'http://sc19h2l.pythonanywhere.com/bookflight/'
        data = {
            'flight_num': flight_num,
            'passenger_name': passenger_name,
            'order_id': order_id,
            'order_price': order_price,
            'ticket_time': ticket_time,
            'payment_status': payment_status
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=data, headers=headers)
        print(data)

        # Check the response status code and format the response message accordingly
        if response.status_code == 200:
            success_msg = f'Booking successful for {passenger_name} on flight {flight_num}'
            return Response({'code': '200', 'msg': success_msg})
        else:
            error_msg = f'Error: {response.status_code} {response.reason}'
            return Response({'code': '400', 'msg': error_msg})


class PaymentMethods(APIView):
    @staticmethod
    def get(request):
        url = 'http://sc19h2l.pythonanywhere.com/paymentmethods/'
        response = requests.get(url)
        print(response.url)

        if response.status_code == 200:
            payment_platform = response.json().get('data', {}).get('payment_platform', [])
            print(payment_platform)
            return Response({'code': '200', 'msg': 'successful', 'payment_platform': payment_platform})
        else:
            error_msg = f'Error: {response.status_code} {response.reason}'
            return Response({'code': '400', 'msg': error_msg})


class PayForBooking(APIView):
    @staticmethod
    def post(request):
        payment_platform = request.data.get('payment_platform')
        order_id = request.data.get('order_id')

        url = 'http://sc19h2l.pythonanywhere.com/payforbooking/'
        headers = {'Content-Type': 'application/json'}
        data = {'payment_platform': payment_platform, 'order_id': order_id}
        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        print(response.url)
        print(response.json())
        print(result['code'])

        if result['code'] == "200":
            response_data = response.json().get('data', {})
            aid = response_data.get('AID')
            pid = response_data.get('PID')
            order_price = response_data.get('order_price')
            return Response({
                'code': '200',
                'msg': 'successful',
                'data': {'AID': aid, 'PID': pid, 'order_price': order_price, 'order_id': order_id}
            })
        elif result['code'] == "503":
            return Response({'code': '400', 'msg': result['msg'], 'error': result['msg']})
        else:
            error_msg = f'Error: {response.status_code} {response.reason}'
            return Response({'code': '400', 'msg': 'fail', 'error': error_msg})


