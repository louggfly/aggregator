import re
from datetime import datetime, timedelta
import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

lowerRegex = re.compile('[a-z]')
upperRegex = re.compile('[A-Z]')
digitRegex = re.compile('[0-9]')

class FindFlight(APIView):
    @staticmethod
    def get(request):
        # Extract query parameters from the request
        departure_date = request.query_params.get('departure_date')
        departure = request.query_params.get('departure')
        arrival = request.query_params.get('arrival')

        # Parse the departure date from the request into a datetime object
        departure_date = datetime.strptime(departure_date, '%Y/%m/%d').date()

        # Query the Flight model for flights matching the specified criteria
        flights = Flight.objects.filter(departure_date=departure_date, departure=departure, arrival=arrival)

        # If there are matching flights, serialize the data and return a response with status 200
        if flights.exists():
            data = []
            for flight in flights:
                data.append({
                    'flight_num': flight.flight_num,
                    'airline': flight.airline,
                    'departure_date': str(flight.departure_date),
                    'departure_time': str(flight.departure_time),
                    'arrive_date': str(flight.arrive_date),
                    'arrive_time': str(flight.arrive_time),
                    'flight_price': flight.flight_price,
                    'seat_number': flight.seat_number,
                    'departure': flight.departure,
                    'arrival': flight.arrival
                })
            return Response({'code': '200', 'msg': 'successful', 'data': data})

        # If there are no matching flights, return a response with status 503 and a message indicating failure
        else:
            return Response({'code': '503', 'msg': 'fail'})

class BookFlight(APIView):
    @staticmethod
    def post(request):
        # Extract the required fields from the request data
        flight_num = request.data.get('flight_num')
        passenger_name = request.data.get('passenger_name')
        order_id = request.data.get('order_id')
        order_price = request.data.get('order_price')
        ticket_time = request.data.get('ticket_time')
        payment_status = request.data.get('payment_status')

        # TODO: Implement payment processing logic

        # Send the response to the client
        response_data = {
            'booking_status': 'booking successful'
        }
        return Response({'code': '200', 'msg': 'successful', 'data': response_data}, status=status.HTTP_200_OK)
