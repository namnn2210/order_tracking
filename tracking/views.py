from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

# Create your views here.
def index(request):
    carriers = {
        'ilyanglogis': 't1',
        'epost': 't2',
        'cjkorex': 't3',
        'hanjin': 'ha',
        'ilogen': 'iln',
        'ems': 'ms',
        'chunil': 'cnil',
        'kunyoung': 'young',
        'fedexkr': 'exkr',
        'ds3211': '211',
        'kdexp': 'exp'
    }
    
    display_carriers = list(carriers.values())
    results = []
    status_count = {
        'Đã_thông_quan': 0,
        'Đang_thông_quan': 0,
        'Đang_vận_chuyển': 0,
        'Đã_giao_hàng': 0,
    }
    status_lists = {
        'Đã_thông_quan': [],
        'Đang_thông_quan': [],
        'Đang_vận_chuyển': [],
        'Đã_giao_hàng': [],
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
                    status_count['Đã_thông_quan'] += 1
                    status_lists['Đã_thông_quan'].append(number)
                elif status_text == 'Đang thông quan':
                    status_count['Đang_thông_quan'] += 1
                    status_lists['Đang_thông_quan'].append(number)
                elif status_text == 'Đang vận chuyển':
                    status_count['Đang_vận_chuyển'] += 1
                    status_lists['Đang_vận_chuyển'].append(number)
                elif status_text == 'Đã giao hàng':
                    status_count['Đã_giao_hàng'] += 1
                    status_lists['Đã_giao_hàng'].append(number)
        
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
