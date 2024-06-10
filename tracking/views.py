from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

# Create your views here.
def index(request):
    carriers = [
        'ilyanglogis',
        'epost',
        'CJ대한통운',
        'hanjin',
        'ilogen',
        'ems',
        'chunil',
        'kunyoung',
        'fedexkr',
        'ds3211',
        'kdexp'
    ]
    results = []
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        list_tracking_number = tracking_number.split('\r\n')
        carrier = request.POST.get('carrier')
        for number in list_tracking_number:
            tracking_url = f'https://track.shiptrack.co.kr/{carrier}/{number}'
            response = requests.get(tracking_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            status = soup.find('div',{'class':'parcel-heading'})
            if status:
                status = translate_status(status.text.strip())
            else:
                status = 'Không xác định'
            results.append({'tracking_number':number,'status':status})
        return render(request, 'index.html',{'results':results,'carriers':carriers})
    return render(request, 'index.html',{'carriers':carriers})

def translate_status(status):
    if status == '수입신고':
        return 'Khai báo nhập khẩu'
    elif status == '입항':
        return 'Nhập cảng'
    elif status == '반입신고' or status == '수입신고수리':
        return 'Đang thông quan'
    elif status == '반출신고':
        return 'Đã thông quan'
    elif status == '간선상차' or status == '집화처리':
        return 'Đang vận chuyển'
    elif status == '배달출발':
        return 'Đang giao hàng'
    elif status == '배달완료':
        return 'Đã giao hàng'
    elif status == '통관중':
        return 'Đang thông quan'
    elif status == '결과없음':
        return 'Chưa có thông tin'
    else:
        return 'Không xác định'
