from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

# Create your views here.
def index(request):
    carriers = {
         'cjkorex': 'CJ 대한통운',
         'hanjin': '한진택배',
         'ilogen': '로젠택배',
         'kdexp': '경동택배',
         'fedexkr': 'FedEx',
         'ilyanglogis': '일양로지스',
         'epost': '우체국택배',
         'ems': 'EMS',
         'chunil': '천일택배',
         'kunyoung': '건영택배',
         'ds3211': '대신택배'       
    }
    
    display_carriers = list(carriers.values())
    results = []
    status_count = {
        'Đã thông quan': 0,
        'Đang thông quan': 0,
        'Đang vận chuyển': 0,
        'Đã giao hàng': 0,
    }
    status_lists = {
        'Đã thông quan': [],
        'Đang thông quan': [],
        'Đang vận chuyển': [],
        'Đã giao hàng': [],
    }
    
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        list_tracking_number = tracking_number.split('\r\n')
        selected_carrier_display = request.POST.get('carrier')
        
        # Get the actual carrier code based on the display value
        carrier = next((key for key, value in carriers.items() if value == selected_carrier_display), None)
        
        if not carrier:
            results.append({'tracking_number': '', 'status': 'Không xác định carrier'})
        else:
            for number in list_tracking_number:
                tracking_url = f'https://track.shiptrack.co.kr/{carrier}/{number}'
                response = requests.get(tracking_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                status = soup.find('div', {'class': 'parcel-heading'})
                if status:
                    status_text = translate_status(status.text.strip())
                else:
                    status_text = 'Không xác định'
                results.append({'tracking_number': number, 'status': status_text})
                
                # Increment status count and add to status list
                if status_text == 'Đã thông quan':
                    status_count['Đã thông quan'] += 1
                    status_lists['Đã thông quan'].append(number)
                elif status_text == 'Đang thông quan':
                    status_count['Đang thông quan'] += 1
                    status_lists['Đang thông quan'].append(number)
                elif status_text == 'Đang vận chuyển':
                    status_count['Đang vận chuyển'] += 1
                    status_lists['Đang vận chuyển'].append(number)
                elif status_text == 'Đã giao hàng':
                    status_count['Đã giao hàng'] += 1
                    status_lists['Đã giao hàng'].append(number)
        
        return render(request, 'index.html', {
            'results': results,
            'carriers': display_carriers,
            'status_count': status_count,
            'status_lists': status_lists,
        })
    
    return render(request, 'index.html', {
        'carriers': display_carriers,
        'status_count': status_count,
        'status_lists': status_lists,
    })

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
