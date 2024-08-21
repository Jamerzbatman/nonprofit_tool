from django.core.management import call_command
from .models import App, Payment
from .forms import AppForm
from django.http import JsonResponse



def format_app_name(app_name):
    # Replace underscores with spaces and capitalize each word
    return app_name.replace('_', ' ').title()

def list_apps(request):
    apps = App.objects.all().values('id', 'name')
    
    # Format app names
    formatted_apps = [
        {
            'id': app['id'],
            'name': format_app_name(app['name'])
        }
        for app in apps
    ]
    
    return JsonResponse({'apps': formatted_apps})


def create_app(request):
    if request.method == 'POST':
        form = AppForm(request.POST)
        if form.is_valid():
            app_name = form.cleaned_data['name']
            app_description = form.cleaned_data['description']

            # Convert app_name to lowercase and replace spaces with underscores
            app_name = app_name.lower().replace(' ', '_')

            # Save the app details to the database
            new_app = App(name=app_name, description=app_description)
            new_app.save()

            # Run the management command to create the app
            try:
                call_command('create_custom_app', app_name, app_description)
                return JsonResponse({'success': True, 'app_id': new_app.id})
            except Exception as e:
                # Optionally, you can remove the app record from the database if the command fails
                new_app.delete()
                return JsonResponse({'success': False, 'error': str(e)})

        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    

def save_payment_details(request, app_id):
    if request.method == 'POST':
        app = App.objects.get(id=app_id)
        payment_type = request.POST.get('payment_type')
        amount = request.POST.get('amount')
        try:
            existing_payment = Payment.objects.filter(app=app, payment_type=payment_type).first()
            if payment_type == 'free':
                Payment.objects.filter(app=app).delete()
                Payment.objects.create(app=app, payment_type=payment_type, amount=00.00)
            elif not payment_type or not amount:
                return JsonResponse({'success': False, 'error': 'Missing payment type or amount'}, status=400)
            elif existing_payment:
                 existing_payment.amount = amount
                 existing_payment.save()

            elif payment_type == 'once':  
                Payment.objects.filter(app=app).delete()
                Payment.objects.create(app=app, payment_type=payment_type, amount=amount)
            else:
                free_payment = Payment.objects.filter(app=app, payment_type='free')
                if free_payment.exists():
                    free_payment.delete()
                once_payment = Payment.objects.filter(app=app, payment_type='once')
                if once_payment.exists():
                    once_payment.delete()
            

                Payment.objects.create(app=app, payment_type=payment_type, amount=amount)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

def delete_payment(request, payment_id):
    if request.method == 'POST':
        try:
            payment = Payment.objects.get(id=payment_id)
            payment.delete()
            return JsonResponse({'success': True})
        except Payment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Payment not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
    

def fetch_payments(request, app_id):
    payments = Payment.objects.filter(app_id=app_id).values('id', 'payment_type', 'amount')
    return JsonResponse({'payments': list(payments)})