import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import *

@csrf_exempt
def save_kakao_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        login_id = data.get('login_id')
        nickname = data.get('nickname')

        try:
            user = User.objects.get(login_id=login_id)
            user.nickname = nickname
            user.save()
            return JsonResponse({'status': 'updated'}, status=200)
        except User.DoesNotExist:
            User.objects.create(
                login_id=login_id,
                nickname=nickname
            )
            return JsonResponse({'status': 'created'}, status=201)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def search_user(request):
    if request.method == 'GET':
        login_id = request.GET.get('loginId')
        try:
            user = User.objects.get(login_id=login_id)
            return JsonResponse({
                'success': True,
                'message': 'User found',
                'data': {
                    'login_id': user.login_id,
                    'nickname': user.nickname
                }
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@api_view(['GET'])
def get_items(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def add_friend(request):
    from_user_id = request.data.get('from_user_id')
    to_user_id = request.data.get('to_user_id')

    try:
        from_user = User.objects.get(login_id=from_user_id)
        to_user = User.objects.get(login_id=to_user_id)

        friend_request, created = Friend.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
            defaults={'are_we_friend': False}
        )

        if created:
            return Response({'status': 'request_sent'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': 'request_already_exists'}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_friends(request, user_id):
    try:
        user = User.objects.get(login_id=user_id)
        friends = Friend.objects.filter(from_user=user, are_we_friend=True).select_related('to_user')
        friend_list = [friend.to_user for friend in friends]
        serializer = UserSerializer(friend_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_friend_requests(request, user_id):
    try:
        user = User.objects.get(login_id=user_id)
        friend_requests = Friend.objects.filter(to_user=user, are_we_friend=False).select_related('from_user')
        request_list = [friend.from_user for friend in friend_requests]
        serializer = UserSerializer(request_list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def accept_friend_request(request):
    from_user_id = request.data.get('from_user_id')
    to_user_id = request.data.get('to_user_id')

    try:
        from_user = User.objects.get(login_id=from_user_id)
        to_user = User.objects.get(login_id=to_user_id)
        friend_request = Friend.objects.get(from_user=from_user, to_user=to_user, are_we_friend=False)
        friend_request.are_we_friend = True
        friend_request.save()
        return Response({'status': 'friend request accepted'}, status=status.HTTP_200_OK)
    except (User.DoesNotExist, Friend.DoesNotExist):
        return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)