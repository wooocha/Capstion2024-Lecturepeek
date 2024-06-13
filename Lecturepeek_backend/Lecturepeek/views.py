from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from .serializers import YouTubeSummarySerializer
from Lecturepeek.service.main import make_note
from Lecturepeek.service.main import load_rand_data
import json


class YouTubeSummaryScriptView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = YouTubeSummarySerializer(data=request.data)
        if serializer.is_valid():
            youtube_link = serializer.validated_data['url']
            try:
                lecture_note = make_note(youtube_link, '1')
                data = json.loads(lecture_note)
                return Response(data, content_type='application/json')
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YouTubeSummarySpeechView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = YouTubeSummarySerializer(data=request.data)
        if serializer.is_valid():
            youtube_link = serializer.validated_data['url']
            try:
                lecture_note = make_note(youtube_link, '2')
                data = json.loads(lecture_note)
                return Response(data, content_type='application/json')
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class YouTubeSummaryRandomView(APIView):
    parser_classes = [JSONParser]
    def post(self, request, *args, **kwargs):
        try:
            lecture_note = load_rand_data()
            data = json.loads(lecture_note)
            return Response(data, content_type='application/json')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
