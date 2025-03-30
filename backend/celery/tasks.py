from celery import shared_task
from backend.models import ServiceProfessional, ServiceRequest
from backend.celery.mail_service import send_email
from sqlalchemy import and_
from flask import render_template
import csv
import os
from datetime import datetime
from flask import current_app


@shared_task(ignore_result = True)
def email_reminder(to, subject, content):
    send_email(to, subject, content)

@shared_task(ignore_result = True)
def send_pending_request_reminders():
    """
    Check for professionals with pending service requests, generate an email
    using the pending_requests_reminder.html template, and send email reminders.
    """
    professionals_with_pending = ServiceProfessional.query.join(
        ServiceRequest, ServiceRequest.pro_id == ServiceProfessional.id
    ).filter(
        ServiceRequest.status == 'requested'
    ).all()
    
    for professional in professionals_with_pending:
        pending_requests = ServiceRequest.query.filter(
            and_(
                ServiceRequest.pro_id == professional.id,
                ServiceRequest.status == 'requested'
            )
        ).all()
        pending_count = len(pending_requests)
        
        if pending_count > 0:
            request_ids = [str(r.id) for r in pending_requests]
            service_names = [r.service.name if hasattr(r, 'service') and r.service else "Service" for r in pending_requests]
            request_dates = [r.request_date.strftime("%Y-%m-%d") if r.request_date else "Recently" for r in pending_requests]
            customer_names = [r.customer.full_name if r.customer and r.customer.full_name else "N/A" for r in pending_requests]
            statuses = [r.status for r in pending_requests]
            expected_completion_dates = [r.completion_date.strftime("%Y-%m-%d") if r.completion_date else "TBD" for r in pending_requests]
            customer_notes = [r.notes if r.notes else "" for r in pending_requests]
            
            subject = f"Reminder: You have {pending_count} pending service requests"
            content = render_template(
                "emails/pending_requests_reminder.html",
                professional_name=professional.full_name,
                count=pending_count,
                request_ids=request_ids,
                service_names=service_names,
                request_dates=request_dates,
                customer_names=customer_names,
                statuses=statuses,
                expected_completion_dates=expected_completion_dates,
                customer_notes=customer_notes,
                dashboard_url="http://localhost:5173/professional/dashboard",
                current_year=2025
            )
            email_reminder.delay(professional.email, subject, content)
    
    return f"Sent reminders to {len(professionals_with_pending)} professionals with pending requests"

@shared_task(ignore_result=True)
def send_monthly_activity_report():
    """
    Generate a monthly activity report for each customer and send it via email.
    """
    from datetime import datetime, timedelta
    from backend.models import Customer, ServiceRequest

    today = datetime.utcnow()
    first_day_of_current = datetime(today.year, today.month, 1)
    last_day_previous = first_day_of_current - timedelta(microseconds=1)
    first_day_previous = datetime(last_day_previous.year, last_day_previous.month, 1)

    customers = Customer.query.all()
    for customer in customers:
        requests = ServiceRequest.query.filter(
            ServiceRequest.customer_id == customer.id,
            ServiceRequest.request_date >= first_day_previous,
            ServiceRequest.request_date <= last_day_previous
        ).all()
        total = len(requests)
        completed = len([r for r in requests if r.status == 'completed'])
        pending = len([r for r in requests if r.status == 'assigned'])
        requested = len([r for r in requests if r.status == 'requested'])
        cancelled = len([r for r in requests if r.status == 'cancelled'])
        
        service_details = []
        for r in requests:
            service_name = r.service.name if r.service and hasattr(r.service, 'name') else "Unknown"
            professional_name = r.professional.full_name if r.professional else "Not Assigned"
            request_date = r.request_date.strftime("%Y-%m-%d") if r.request_date else "N/A"
            completion_date = r.completion_date.strftime("%Y-%m-%d") if r.completion_date else "N/A"
            assigned_date = r.assigned_date.strftime("%Y-%m-%d") if r.assigned_date else "N/A"
            completed_on = r.completed_on.strftime("%Y-%m-%d") if r.completed_on else "N/A"
            cancelled_on = r.cancelled_on.strftime("%Y-%m-%d") if r.cancelled_on else "N/A"
            service_details.append({
                'service_name': service_name,
                'request_date': request_date,
                'completion_date': completion_date,
                'assigned_date': assigned_date,
                'completed_on': completed_on,
                'cancelled_on': cancelled_on,
                'cancelled_by': r.cancelled_by or "N/A",
                'status': r.status,
                'professional_name': professional_name
            })

        subject = f"Your Monthly Activity Report: {first_day_previous.strftime('%B %Y')}"
        content = render_template(
            "emails/monthly_activity_report.html",
            customer_name=customer.full_name,
            total_requests=total,
            completed_requests=completed,
            pending_requests=pending,
            requested_requests=requested,
            cancelled_requests=cancelled,
            service_details=service_details,
            month=first_day_previous.strftime('%B %Y'),
            current_year=datetime.utcnow().year
        )
        email_reminder.delay(customer.email, subject, content)
    return f"Monthly activity reports sent to {len(customers)} customers"

@shared_task(ignore_result=True)
def export_service_requests_csv():
    file_dir = os.path.join(os.path.dirname(__file__), "user-downloads")
    os.makedirs(file_dir, exist_ok=True)
    filename = f"service_requests_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(file_dir, filename)
    requests = ServiceRequest.query.filter(ServiceRequest.status=='completed').all()
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["service_id", "customer_id", "pro_id", "request_date", "status", "notes"])
        for req in requests:
            request_date = req.request_date.strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([req.service_id, req.customer_id, req.pro_id, request_date, req.status, req.notes or ""])
    
    admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@housecare.com')
    subject = "CSV Export - Service Requests"
    app_base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    file_url = f"{app_base_url}/backend/celery/user-downloads/{filename}"
    content = render_template(
        "emails/export_service_requests.html",
        download_link=file_url
    )
    send_email(admin_email, subject, content)
    
    return f"CSV file exported: {filename}"