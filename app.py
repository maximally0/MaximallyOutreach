import os
import json
import csv
import io
import logging
import random
import re
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import pandas as pd
import resend
from email_validator import validate_email, EmailNotValidError

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize Resend
resend.api_key = os.environ.get("RESEND_API_KEY", "re_default_key")

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

def load_json_file(filename, default=None):
    """Load JSON file with fallback to default value"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else []

def save_json_file(filename, data):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def initialize_templates():
    """Initialize email templates if they don't exist"""
    templates_file = 'data/templates.json'
    default_templates = [
        {
            "id": 1,
            "name": "Introduction Template",
            "subject": "Partnership Opportunity with {{school_name}}",
            "content": "Dear {{contact_person}},\n\nI hope this email finds you well. My name is [Your Name] and I'm reaching out from Maximally to explore a potential partnership with {{school_name}} in {{city}}.\n\nWe specialize in educational technology solutions that can help enhance student learning outcomes. I'd love to discuss how we can support {{school_name}}'s educational goals.\n\nWould you be available for a brief call next week?\n\nBest regards,\n[Your Name]\nMaximally Team"
        },
        {
            "id": 2,
            "name": "Product Demo Template",
            "subject": "Free Demo for {{school_name}} - Educational Technology",
            "content": "Hello {{contact_person}},\n\nI wanted to reach out to {{school_name}} in {{city}} to offer a complimentary demonstration of our educational platform.\n\nOur solution has helped schools increase student engagement by 40% on average. I believe {{school_name}} could greatly benefit from our technology.\n\nCould we schedule a 15-minute demo at your convenience?\n\nThank you for your time,\n[Your Name]\nMaximally"
        },
        {
            "id": 3,
            "name": "Follow-up Template",
            "subject": "Following up on our conversation - {{school_name}}",
            "content": "Hi {{contact_person}},\n\nI wanted to follow up on my previous email regarding the partnership opportunity with {{school_name}}.\n\nI understand you're busy managing {{school_name}} in {{city}}, but I believe our platform could provide significant value to your students and teachers.\n\nWould you prefer a quick phone call or email exchange to discuss this further?\n\nLooking forward to hearing from you,\n[Your Name]\nMaximally"
        },
        {
            "id": 4,
            "name": "Case Study Template",
            "subject": "How Schools Like {{school_name}} Improved Student Outcomes",
            "content": "Dear {{contact_person}},\n\nI hope you're having a great week at {{school_name}}!\n\nI wanted to share a success story from a school similar to yours in {{city}}. They saw a 35% improvement in student performance after implementing our platform.\n\nI'd love to discuss how {{school_name}} could achieve similar results. Are you available for a brief conversation this week?\n\nBest,\n[Your Name]\nMaximally Team"
        },
        {
            "id": 5,
            "name": "Value Proposition Template",
            "subject": "Transform Education at {{school_name}} with Maximally",
            "content": "Hello {{contact_person}},\n\nAs an educational leader at {{school_name}} in {{city}}, you're always looking for ways to improve student outcomes.\n\nOur platform offers:\n- Interactive learning modules\n- Real-time progress tracking\n- Personalized learning paths\n- Teacher analytics dashboard\n\nWould you like to see how {{school_name}} could benefit? I can arrange a personalized demo.\n\nWarm regards,\n[Your Name]\nMaximally"
        },
        {
            "id": 6,
            "name": "Urgent Opportunity Template",
            "subject": "Limited Time: Special Offer for {{school_name}}",
            "content": "Hi {{contact_person}},\n\nI have exciting news for {{school_name}}! We're offering a limited-time pilot program for select schools in {{city}}.\n\nThis program includes:\n- Free 3-month trial\n- Dedicated support team\n- Custom training for your staff\n- Performance analytics\n\nOnly 5 spots remaining. Is {{school_name}} interested in being part of this exclusive program?\n\nBest regards,\n[Your Name]\nMaximally"
        },
        {
            "id": 7,
            "name": "Research-Based Template",
            "subject": "Evidence-Based Solutions for {{school_name}}",
            "content": "Dear {{contact_person}},\n\nRecent educational research shows that technology-enhanced learning can improve student engagement by up to 60%.\n\nAt {{school_name}} in {{city}}, I believe you're committed to giving students the best possible education. Our research-backed platform aligns with this mission.\n\nWould you like to review the research findings and see how they apply to {{school_name}}?\n\nSincerely,\n[Your Name]\nMaximally Research Team"
        },
        {
            "id": 8,
            "name": "Personal Connection Template",
            "subject": "Supporting {{school_name}}'s Educational Mission",
            "content": "Hello {{contact_person}},\n\nAs someone passionate about education, I was impressed by {{school_name}}'s commitment to student success in {{city}}.\n\nI believe our platform could amplify the great work you're already doing at {{school_name}}. We've helped similar schools enhance their educational programs significantly.\n\nI'd love to learn more about {{school_name}}'s specific goals and see how we can support them.\n\nCould we schedule a brief call?\n\nBest wishes,\n[Your Name]\nMaximally"
        },
        {
            "id": 9,
            "name": "Problem-Solution Template",
            "subject": "Solving Common Challenges at {{school_name}}",
            "content": "Hi {{contact_person}},\n\nMany schools in {{city}} face similar challenges: keeping students engaged, tracking progress effectively, and supporting diverse learning needs.\n\nI'd like to show you how {{school_name}} can address these challenges with our comprehensive platform. We've developed solutions specifically for schools like yours.\n\nAre you available for a 20-minute discussion about {{school_name}}'s current challenges and our solutions?\n\nThank you,\n[Your Name]\nMaximally Solutions Team"
        },
        {
            "id": 10,
            "name": "Community Impact Template",
            "subject": "Empowering {{school_name}} to Shape the Future",
            "content": "Dear {{contact_person}},\n\n{{school_name}} plays a vital role in shaping the future of students in {{city}}. We want to support that mission.\n\nOur educational platform has helped schools create more engaging, effective learning environments. Students at partner schools report higher satisfaction and better outcomes.\n\nI'd love to discuss how {{school_name}} could join our community of forward-thinking educational institutions.\n\nWhen would be a good time to connect?\n\nWith appreciation,\n[Your Name]\nMaximally Community Team"
        }
    ]

    if not os.path.exists(templates_file):
        save_json_file(templates_file, default_templates)
    return load_json_file(templates_file, default_templates)

def validate_email_address(email):
    """Validate email address format"""
    try:
        # Validate and get info about the email
        validated_email = validate_email(email)
        return True, validated_email.email
    except EmailNotValidError:
        return False, email

def replace_placeholders(text, school_data):
    """Replace placeholders in email content with school data"""
    placeholders = {
        '{{school_name}}': school_data.get('School Name', ''),
        '{{contact_person}}': school_data.get('Contact Person', ''),
        '{{city}}': school_data.get('City', ''),
        '{{email}}': school_data.get('Email', '')
    }

    result = text
    for placeholder, value in placeholders.items():
        result = result.replace(placeholder, str(value))

    return result

def load_settings():
    """Load email settings from file"""
    return load_json_file('data/settings.json', {})

@app.route('/')
def index():
    """Main dashboard page"""
    schools = load_json_file('data/schools.json', [])
    templates = load_json_file('data/templates.json', [])
    logs = load_json_file('data/logs.json', [])

    return render_template('index.html', 
                         schools=schools, 
                         templates=templates, 
                         logs=logs)

@app.route('/upload', methods=['POST'])
def upload_csv():
    """Handle CSV file upload"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))

        if not file.filename or not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(url_for('index'))

        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)

        schools = []
        invalid_emails = []
        for row in csv_input:
            # Clean and validate row data
            school = {key.strip(): value.strip() for key, value in row.items() if value.strip()}
            if school.get('School Name') and school.get('Email'):
                # Validate email format
                is_valid, clean_email = validate_email_address(school['Email'])
                if is_valid:
                    school['Email'] = clean_email  # Use cleaned email
                    schools.append(school)
                else:
                    invalid_emails.append({'school': school.get('School Name', 'Unknown'), 'email': school.get('Email', '')})
                    logging.warning(f"Invalid email for {school.get('School Name', 'Unknown')}: {school.get('Email', '')}")

        if not schools:
            flash('No valid school records found in CSV. Make sure you have School Name and Email columns.', 'error')
            return redirect(url_for('index'))

        # Save schools data
        save_json_file('data/schools.json', schools)
        
        # Report results with validation info
        success_msg = f'Successfully uploaded {len(schools)} schools'
        if invalid_emails:
            success_msg += f' ({len(invalid_emails)} schools skipped due to invalid emails)'
            logging.info(f"Skipped schools with invalid emails: {invalid_emails}")
        flash(success_msg, 'success')

    except Exception as e:
        logging.error(f"Error uploading CSV: {str(e)}")
        flash(f'Error uploading file: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/preview', methods=['POST'])
def preview_email():
    """Preview email with replaced placeholders"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        school_index = data.get('school_index', 0)
        custom_content = data.get('custom_content')
        custom_subject = data.get('custom_subject')
        custom_html_content = data.get('custom_html_content')

        schools = load_json_file('data/schools.json', [])
        templates = load_json_file('data/templates.json', [])

        if not schools:
            return jsonify({'error': 'No schools uploaded'}), 400

        if school_index >= len(schools):
            return jsonify({'error': 'Invalid school index'}), 400

        school = schools[school_index]

        # Find template
        template = None
        for t in templates:
            if t['id'] == template_id:
                template = t
                break

        if not template:
            return jsonify({'error': 'Template not found'}), 400

        # Use custom content if provided, otherwise use template
        subject = custom_subject if custom_subject else template['subject']
        content = custom_content if custom_content else template['content']
        html_content = custom_html_content if custom_html_content else template.get('content_html', '')

        # Replace placeholders
        preview_subject = replace_placeholders(subject, school)
        preview_content = replace_placeholders(content, school)
        preview_html = replace_placeholders(html_content, school) if html_content else ''

        return jsonify({
            'subject': preview_subject,
            'content': preview_content,
            'html_content': preview_html,
            'school': school
        })

    except Exception as e:
        logging.error(f"Error previewing email: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/send', methods=['POST'])
def send_emails():
    """Send emails to selected schools"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        selected_schools = data.get('selected_schools', [])
        ab_testing = data.get('ab_testing', False)
        custom_content = data.get('custom_content')
        custom_subject = data.get('custom_subject')
        custom_html_content = data.get('custom_html_content')

        schools = load_json_file('data/schools.json', [])
        templates = load_json_file('data/templates.json', [])
        logs = load_json_file('data/logs.json', [])

        if not selected_schools:
            return jsonify({'error': 'No schools selected'}), 400

        # For large-scale sending, allow bigger batches but with better rate limiting
        if len(selected_schools) > 500:
            return jsonify({'error': 'Please select 500 or fewer schools at a time to prevent system overload'}), 400

        results = []

        for i, school_index in enumerate(selected_schools):
            if school_index >= len(schools):
                continue

            school = schools[school_index]
            
            # Pre-validate email before attempting to send
            is_valid, clean_email = validate_email_address(school['Email'])
            if not is_valid:
                log_entry = {
                    'school_name': school.get('School Name', ''),
                    'email': school['Email'],
                    'template_used': '',
                    'template_id': 0,
                    'status': 'Error (Invalid Email): Email format is invalid',
                    'timestamp': datetime.now().isoformat(),
                    'email_id': '',
                    'subject': '',
                    'error_category': 'Invalid Email'
                }
                logs.append(log_entry)
                results.append({'status': 'error', 'school': school['School Name'], 'error': 'Invalid email format', 'category': 'Invalid Email'})
                continue
            
            # Use cleaned email
            school['Email'] = clean_email

            # Determine which template to use
            if ab_testing:
                # Random template selection for A/B testing
                current_template = random.choice(templates)
            else:
                # Use specified template
                current_template = None
                for t in templates:
                    if t['id'] == template_id:
                        current_template = t
                        break

                if not current_template:
                    return jsonify({'error': 'Template not found'}), 400

            # Use custom content if provided
            subject = custom_subject if custom_subject else current_template['subject']
            content = custom_content if custom_content else current_template.get('content_text', current_template['content'])
            html_content = custom_html_content if custom_html_content else current_template.get('content_html', '')

            # Replace placeholders
            email_subject = replace_placeholders(subject, school)
            email_content = replace_placeholders(content, school)
            email_html = replace_placeholders(html_content, school) if html_content else ''

            # Improved rate limiting for large volumes
            # Resend allows 10 emails/second for most plans, so we use 0.2s delay
            if i > 0:
                time.sleep(0.2)  # 5 emails per second, well within limits
                
            # Progress logging for large batches
            if i > 0 and i % 100 == 0:
                logging.info(f"Progress: {i}/{len(selected_schools)} emails processed")

            # Send email via Resend with timeout handling
            try:
                settings = load_settings()
                sender_email = settings.get('sender_email', 'hello@maximally.in')
                sender_name = settings.get('sender_name', 'Maximally Team')
                from_address = f"{sender_name} <{sender_email}>" if sender_name else sender_email

                params = {
                    "from": from_address,
                    "to": [school['Email']],
                    "subject": email_subject,
                }

                if email_html:
                    params["html"] = email_html
                    if email_content:
                        params["text"] = email_content
                else:
                    params["text"] = email_content

                # Enhanced retry logic for production use
                max_retries = 3
                base_retry_delay = 1
                
                for attempt in range(max_retries):
                    try:
                        email = resend.Emails.send(params)
                        break  # Success, exit retry loop
                    except Exception as retry_error:
                        retry_error_str = str(retry_error)
                        
                        # Handle specific error types
                        if "rate limit" in retry_error_str.lower() or "too many requests" in retry_error_str:
                            # Exponential backoff for rate limits
                            wait_time = base_retry_delay * (2 ** attempt) + random.uniform(0, 1)
                            logging.warning(f"Rate limit hit on attempt {attempt + 1} for {school['Email']}, waiting {wait_time:.1f}s")
                            time.sleep(wait_time)
                        elif "invalid" in retry_error_str.lower() and "email" in retry_error_str.lower():
                            # Don't retry invalid emails
                            logging.error(f"Invalid email address {school['Email']}: {retry_error_str}")
                            raise retry_error
                        else:
                            # Standard retry delay for other errors
                            wait_time = base_retry_delay * (attempt + 1)
                            logging.warning(f"Attempt {attempt + 1} failed for {school['Email']}: {retry_error_str}")
                            if attempt < max_retries - 1:
                                time.sleep(wait_time)
                        
                        if attempt == max_retries - 1:
                            raise retry_error  # Re-raise on final attempt

                log_entry = {
                    'school_name': school.get('School Name', ''),
                    'email': school['Email'],
                    'template_used': current_template['name'],
                    'template_id': current_template['id'],
                    'status': 'Sent',
                    'timestamp': datetime.now().isoformat(),
                    'email_id': email.get('id', ''),
                    'subject': email_subject
                }

                results.append({'status': 'success', 'school': school['School Name']})

            except Exception as email_error:
                error_message = str(email_error)
                logging.error(f"Error sending email to {school['Email']}: {error_message}")
                
                # Enhanced error categorization and logging
                error_category = "Unknown Error"
                
                if "rate limit" in error_message.lower() or "too many requests" in error_message:
                    error_category = "Rate Limit"
                elif "invalid" in error_message.lower() and "email" in error_message.lower():
                    error_category = "Invalid Email"
                elif "authentication" in error_message.lower() or "unauthorized" in error_message.lower():
                    error_category = "Authentication Error"
                elif "network" in error_message.lower() or "connection" in error_message.lower():
                    error_category = "Network Error"
                
                log_entry = {
                    'school_name': school.get('School Name', ''),
                    'email': school['Email'],
                    'template_used': current_template['name'],
                    'template_id': current_template['id'],
                    'status': f'Error ({error_category}): {error_message}',
                    'timestamp': datetime.now().isoformat(),
                    'email_id': '',
                    'subject': email_subject,
                    'error_category': error_category
                }
                results.append({'status': 'error', 'school': school['School Name'], 'error': error_message, 'category': error_category})

            logs.append(log_entry)

        # Save updated logs
        save_json_file('data/logs.json', logs)

        # Remove successfully sent schools from the schools list
        successful_emails = [result['school'] for result in results if result['status'] == 'success']
        if successful_emails:
            schools = load_json_file('data/schools.json')
            # Keep only schools that were not successfully sent emails
            remaining_schools = [school for school in schools if school.get('School Name', '') not in successful_emails]
            save_json_file('data/schools.json', remaining_schools)

        # Calculate summary statistics
        total_processed = len(results)
        successful_count = len([r for r in results if r['status'] == 'success'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        # Group errors by category for better reporting
        error_categories = {}
        for result in results:
            if result['status'] == 'error':
                category = result.get('category', 'Unknown')
                error_categories[category] = error_categories.get(category, 0) + 1
        
        summary_message = f'Batch completed: {successful_count} sent, {error_count} failed out of {total_processed} schools'
        if error_categories:
            error_details = ', '.join([f"{count} {category}" for category, count in error_categories.items()])
            summary_message += f'. Errors: {error_details}'
        
        logging.info(f"Batch summary: {summary_message}")
        
        return jsonify({
            'message': summary_message,
            'results': results,
            'summary': {
                'total_processed': total_processed,
                'successful': successful_count,
                'failed': error_count,
                'removed_schools': len(successful_emails),
                'error_categories': error_categories
            }
        })

    except Exception as e:
        logging.error(f"Error sending emails: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/error_dashboard')
def error_dashboard():
    """Error Logging Dashboard for Email Campaigns"""
    try:
        logs = load_json_file('data/logs.json', [])
        
        # Filter and analyze error logs
        error_logs = [log for log in logs if 'Error' in log.get('status', '')]
        success_logs = [log for log in logs if log.get('status') == 'Sent' or 'Sent (Retry)' in log.get('status', '')]
        
        # Calculate error statistics
        total_emails = len(logs)
        total_errors = len(error_logs)
        total_success = len(success_logs)
        error_rate = (total_errors / total_emails * 100) if total_emails > 0 else 0
        
        # Group errors by category
        error_categories = {}
        for log in error_logs:
            category = log.get('error_category', 'Unknown')
            if category not in error_categories:
                error_categories[category] = {
                    'count': 0,
                    'examples': []
                }
            error_categories[category]['count'] += 1
            if len(error_categories[category]['examples']) < 5:  # Keep up to 5 examples
                error_categories[category]['examples'].append(log)
        
        # Group errors by template
        template_errors = {}
        for log in error_logs:
            template_name = log.get('template_used', 'Unknown Template')
            template_errors[template_name] = template_errors.get(template_name, 0) + 1
        
        # Recent errors (last 24 hours)
        from datetime import datetime, timedelta
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=24)
        
        recent_errors = []
        for log in error_logs:
            try:
                log_time = datetime.fromisoformat(log.get('timestamp', ''))
                if log_time >= recent_cutoff:
                    recent_errors.append(log)
            except:
                continue
        
        # Timeline data for charts (group by hour for last 24 hours)
        timeline_data = {}
        for i in range(24):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            hour_key = hour_start.strftime('%H:00')
            
            hour_errors = 0
            hour_success = 0
            
            for log in logs:
                try:
                    log_time = datetime.fromisoformat(log.get('timestamp', ''))
                    if hour_start <= log_time < hour_end:
                        if 'Error' in log.get('status', ''):
                            hour_errors += 1
                        elif log.get('status') == 'Sent' or 'Sent (Retry)' in log.get('status', ''):
                            hour_success += 1
                except:
                    continue
            
            timeline_data[hour_key] = {
                'errors': hour_errors,
                'success': hour_success
            }
        
        return render_template('error_dashboard.html',
                             error_logs=error_logs,
                             success_logs=success_logs,
                             total_emails=total_emails,
                             total_errors=total_errors,
                             total_success=total_success,
                             error_rate=error_rate,
                             error_categories=error_categories,
                             template_errors=template_errors,
                             recent_errors=recent_errors,
                             timeline_data=timeline_data)
    
    except Exception as e:
        logging.error(f"Error loading error dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/error_stats')
def get_error_stats():
    """API endpoint for error statistics"""
    try:
        logs = load_json_file('data/logs.json', [])
        
        # Calculate basic stats
        total_emails = len(logs)
        error_logs = [log for log in logs if 'Error' in log.get('status', '')]
        success_logs = [log for log in logs if log.get('status') == 'Sent' or 'Sent (Retry)' in log.get('status', '')]
        
        # Group errors by category
        error_categories = {}
        for log in error_logs:
            category = log.get('error_category', 'Unknown')
            error_categories[category] = error_categories.get(category, 0) + 1
        
        return jsonify({
            'total_emails': total_emails,
            'total_errors': len(error_logs),
            'total_success': len(success_logs),
            'error_rate': (len(error_logs) / total_emails * 100) if total_emails > 0 else 0,
            'error_categories': error_categories
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_errors', methods=['POST'])
def clear_errors():
    """Clear all error logs"""
    try:
        logs = load_json_file('data/logs.json', [])
        # Keep only successful sends
        success_logs = [log for log in logs if log.get('status') == 'Sent' or 'Sent (Retry)' in log.get('status', '')]
        save_json_file('data/logs.json', success_logs)
        
        flash(f'Cleared {len(logs) - len(success_logs)} error logs', 'success')
        return redirect(url_for('error_dashboard'))
    
    except Exception as e:
        logging.error(f"Error clearing error logs: {str(e)}")
        flash(f'Error clearing logs: {str(e)}', 'error')
        return redirect(url_for('error_dashboard'))

@app.route('/export')
def export_logs():
    """Export email logs as CSV"""
    try:
        logs = load_json_file('data/logs.json', [])

        if not logs:
            flash('No email logs to export', 'error')
            return redirect(url_for('index'))

        # Create CSV content
        output = io.StringIO()
        fieldnames = ['school_name', 'email', 'template_used', 'status', 'timestamp', 'subject']
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()
        for log in logs:
            writer.writerow({
                'school_name': log.get('school_name', ''),
                'email': log.get('email', ''),
                'template_used': log.get('template_used', ''),
                'status': log.get('status', ''),
                'timestamp': log.get('timestamp', ''),
                'subject': log.get('subject', '')
            })

        # Create file-like object
        output.seek(0)
        file_data = io.BytesIO()
        file_data.write(output.getvalue().encode('utf-8'))
        file_data.seek(0)

        return send_file(
            file_data,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'email_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    except Exception as e:
        logging.error(f"Error exporting logs: {str(e)}")
        flash(f'Error exporting logs: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear all data (schools, logs)"""
    try:
        save_json_file('data/schools.json', [])
        save_json_file('data/logs.json', [])
        flash('All data cleared successfully', 'success')
    except Exception as e:
        logging.error(f"Error clearing data: {str(e)}")
        flash(f'Error clearing data: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/edit_template/<int:template_id>')
def edit_template(template_id):
    """Edit template page"""
    templates = load_json_file('data/templates.json', [])
    template = None
    for t in templates:
        if t['id'] == template_id:
            template = t
            break

    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('index'))

    return render_template('edit_template.html', template=template)

@app.route('/save_template', methods=['POST'])
def save_template():
    """Save template changes"""
    try:
        template_id = int(request.form.get('template_id'))
        name = request.form.get('name', '').strip()
        subject = request.form.get('subject', '').strip()
        content = request.form.get('content', '').strip()
        content_text = request.form.get('content_text', '').strip()
        content_html = request.form.get('content_html', '').strip()

        # Use the submitted content, or fall back to separate text/html fields
        final_content = content if content else (content_text if content_text else content_html)

        if not all([name, subject, final_content]):
            flash('All fields are required', 'error')
            return redirect(url_for('edit_template', template_id=template_id))

        templates = load_json_file('data/templates.json', [])

        # Update template with both text and HTML content
        for i, template in enumerate(templates):
            if template['id'] == template_id:
                templates[i] = {
                    'id': template_id,
                    'name': name,
                    'subject': subject,
                    'content': final_content,
                    'content_text': content_text,
                    'content_html': content_html
                }
                break

        save_json_file('data/templates.json', templates)
        flash('Template updated successfully', 'success')

    except Exception as e:
        logging.error(f"Error saving template: {str(e)}")
        flash(f'Error saving template: {str(e)}', 'error')

    return redirect(url_for('index'))

@app.route('/create_template', methods=['GET', 'POST'])
def create_template():
    """Create new template"""
    if request.method == 'GET':
        return render_template('create_template.html')

    try:
        name = request.form.get('name', '').strip()
        subject = request.form.get('subject', '').strip()
        content = request.form.get('content', '').strip()
        content_text = request.form.get('content_text', '').strip()
        content_html = request.form.get('content_html', '').strip()

        # Use the submitted content, or fall back to separate text/html fields
        final_content = content if content else (content_text if content_text else content_html)

        if not all([name, subject, final_content]):
            flash('All fields are required', 'error')
            return render_template('create_template.html')

        templates = load_json_file('data/templates.json', [])

        # Find next ID
        next_id = max([t['id'] for t in templates], default=0) + 1

        # Create new template with both text and HTML content
        new_template = {
            'id': next_id,
            'name': name,
            'subject': subject,
            'content': final_content,
            'content_text': content_text,
            'content_html': content_html
        }

        templates.append(new_template)
        save_json_file('data/templates.json', templates)

        flash('Template created successfully', 'success')
        return redirect(url_for('index'))

    except Exception as e:
        logging.error(f"Error creating template: {str(e)}")
        flash(f'Error creating template: {str(e)}', 'error')
        return render_template('create_template.html')

@app.route('/delete_template/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    """Delete a template"""
    try:
        templates = load_json_file('data/templates.json', [])
        
        # Find and remove template
        templates = [t for t in templates if t['id'] != template_id]
        
        save_json_file('data/templates.json', templates)
        flash('Template deleted successfully', 'success')
        
    except Exception as e:
        logging.error(f"Error deleting template: {str(e)}")
        flash(f'Error deleting template: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/send_test_email', methods=['POST'])
def send_test_email():
    """Send test email with current template content to rishulchanana36@gmail.com"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        custom_subject = data.get('subject', '')
        custom_content = data.get('content', '')
        html_content = data.get('html_content', '')
        
        # Get template data if template_id is provided
        template_name = 'Custom Test'
        if template_id:
            templates = load_json_file('data/templates.json', [])
            template = None
            for t in templates:
                if t['id'] == template_id:
                    template = t
                    break
            
            if template:
                template_name = template['name']
                # Use template content if no custom content provided
                if not custom_subject:
                    custom_subject = template['subject']
                if not custom_content and not html_content:
                    custom_content = template['content']
                    # Also check for separate HTML content
                    if template.get('content_html'):
                        html_content = template['content_html']
                    if template.get('content_text'):
                        custom_content = template['content_text']
        
        # Use current form content (from the template editor or custom form)
        subject = custom_subject if custom_subject else 'Test Email from Maximally Dashboard'
        content = custom_content if custom_content else 'This is a test email from your Maximally outreach dashboard.'
        
        # Create sample school data for placeholder replacement
        sample_school = {
            'School Name': 'Sample High School',
            'Contact Person': 'Test Contact',
            'City': 'Test City',
            'Email': 'contact@sampleschool.edu'
        }
        
        # Replace placeholders with sample data
        final_subject = replace_placeholders(subject, sample_school)
        final_content = replace_placeholders(content, sample_school)
        final_html = replace_placeholders(html_content, sample_school) if html_content else ''

        # Get settings for sender info
        settings = load_settings()
        sender_email = settings.get('sender_email', 'hello@maximally.in')
        sender_name = settings.get('sender_name', 'Maximally Team')
        from_address = f"{sender_name} <{sender_email}>" if sender_name else sender_email

        # Send email via Resend
        params = {
            "from": from_address,
            "to": ["rishulchanana36@gmail.com"],
            "subject": f"[TEST] {final_subject}",
        }

        if final_html:
            params["html"] = final_html
            if final_content:
                params["text"] = final_content
        else:
            params["text"] = final_content

        email = resend.Emails.send(params)

        # Log the test email
        logs = load_json_file('data/logs.json', [])
        log_entry = {
            'school_name': 'Test Email',
            'email': 'rishulchanana36@gmail.com',
            'template_used': template_name,
            'template_id': template_id or 0,
            'status': 'Sent (Test)',
            'timestamp': datetime.now().isoformat(),
            'email_id': email.get('id', ''),
            'subject': f"[TEST] {final_subject}"
        }
        logs.append(log_entry)
        save_json_file('data/logs.json', logs)

        return jsonify({
            'message': f'Test email sent successfully using "{template_name}" template',
            'email_id': email.get('id', '')
        })

    except Exception as e:
        logging.error(f"Error sending test email: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/send_custom_email', methods=['POST'])
def send_custom_email():
    """Send custom email without using templates"""
    try:
        data = request.get_json()
        subject = data.get('subject', '').strip()
        content = data.get('content', '').strip()
        html_content = data.get('html_content', '').strip()
        selected_schools = data.get('selected_schools', [])

        if not subject or (not content and not html_content):
            return jsonify({'error': 'Subject and content are required'}), 400

        if not selected_schools:
            return jsonify({'error': 'No schools selected'}), 400

        schools = load_json_file('data/schools.json', [])
        logs = load_json_file('data/logs.json', [])
        results = []

        for i, school_index in enumerate(selected_schools):
            if school_index >= len(schools):
                continue

            school = schools[school_index]

            # Replace placeholders in custom content
            email_subject = replace_placeholders(subject, school)
            email_content = replace_placeholders(content, school) if content else ''
            email_html = replace_placeholders(html_content, school) if html_content else ''

            # Rate limiting: wait 0.6 seconds between emails
            if i > 0:
                time.sleep(0.6)

            # Send email via Resend
            try:
                settings = load_settings()
                sender_email = settings.get('sender_email', 'hello@maximally.in')
                sender_name = settings.get('sender_name', 'Maximally Team')
                from_address = f"{sender_name} <{sender_email}>" if sender_name else sender_email

                params = {
                    "from": from_address,
                    "to": [school['Email']],
                    "subject": email_subject,
                }

                if email_html:
                    params["html"] = email_html
                    if email_content:
                        params["text"] = email_content
                else:
                    params["text"] = email_content

                email = resend.Emails.send(params)

                log_entry = {
                    'school_name': school.get('School Name', ''),
                    'email': school['Email'],
                    'template_used': 'Custom Email',
                    'template_id': 0,
                    'status': 'Sent',
                    'timestamp': datetime.now().isoformat(),
                    'email_id': email.get('id', ''),
                    'subject': email_subject
                }

                results.append({'status': 'success', 'school': school['School Name']})

            except Exception as email_error:
                error_message = str(email_error)
                logging.error(f"Error sending custom email to {school['Email']}: {error_message}")
                
                # If it's a rate limit error, wait and retry once
                if "Too many requests" in error_message or "rate limit" in error_message.lower():
                    logging.info(f"Rate limit hit, waiting 2 seconds and retrying for {school['Email']}")
                    time.sleep(2)
                    try:
                        email = resend.Emails.send(params)
                        log_entry = {
                            'school_name': school.get('School Name', ''),
                            'email': school['Email'],
                            'template_used': 'Custom Email',
                            'template_id': 0,
                            'status': 'Sent (Retry)',
                            'timestamp': datetime.now().isoformat(),
                            'email_id': email.get('id', ''),
                            'subject': email_subject
                        }
                        results.append({'status': 'success', 'school': school['School Name']})
                    except Exception as retry_error:
                        log_entry = {
                            'school_name': school.get('School Name', ''),
                            'email': school['Email'],
                            'template_used': 'Custom Email', 
                            'template_id': 0,
                            'status': f'Error: {str(retry_error)}',
                            'timestamp': datetime.now().isoformat(),
                            'email_id': '',
                            'subject': email_subject
                        }
                        results.append({'status': 'error', 'school': school['School Name'], 'error': str(retry_error)})
                else:
                    log_entry = {
                        'school_name': school.get('School Name', ''),
                        'email': school['Email'],
                        'template_used': 'Custom Email',
                        'template_id': 0,
                        'status': f'Error: {error_message}',
                        'timestamp': datetime.now().isoformat(),
                        'email_id': '',
                        'subject': email_subject
                    }
                    results.append({'status': 'error', 'school': school['School Name'], 'error': error_message})

            logs.append(log_entry)

        # Save updated logs
        save_json_file('data/logs.json', logs)

        # Remove successfully sent schools from the schools list
        successful_emails = [result['school'] for result in results if result['status'] == 'success']
        if successful_emails:
            schools = load_json_file('data/schools.json')
            # Keep only schools that were not successfully sent emails
            remaining_schools = [school for school in schools if school.get('School Name', '') not in successful_emails]
            save_json_file('data/schools.json', remaining_schools)

        return jsonify({
            'message': f'Custom email sending completed. Removed {len(successful_emails)} schools from list.',
            'results': results,
            'removed_schools': len(successful_emails)
        })

    except Exception as e:
        logging.error(f"Error sending custom emails: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Email settings page"""
    if request.method == 'GET':
        current_settings = load_settings()
        return render_template('settings.html', settings=current_settings)

    try:
        sender_email = request.form.get('sender_email', '').strip()
        sender_name = request.form.get('sender_name', '').strip()

        if not sender_email:
            flash('Sender email is required', 'error')
            return redirect(url_for('settings'))

        settings = {
            'sender_email': sender_email,
            'sender_name': sender_name
        }

        save_json_file('data/settings.json', settings)
        flash('Settings updated successfully', 'success')

    except Exception as e:
        logging.error(f"Error saving settings: {str(e)}")
        flash(f'Error saving settings: {str(e)}', 'error')

    return redirect(url_for('settings'))

@app.route('/individual_email', methods=['GET', 'POST'])
def individual_email():
    """Send individual email page"""
    if request.method == 'GET':
        return render_template('individual_email.html')

    try:
        to_email = request.form.get('to_email', '').strip()
        to_name = request.form.get('to_name', '').strip()
        subject = request.form.get('subject', '').strip()
        content = request.form.get('content', '').strip()
        html_content = request.form.get('html_content', '').strip()

        if not all([to_email, subject]) or (not content and not html_content):
            flash('To email, subject, and content are required', 'error')
            return render_template('individual_email.html')

        # Send email via Resend
        settings = load_settings()
        sender_email = settings.get('sender_email', 'hello@maximally.in')
        sender_name = settings.get('sender_name', 'Maximally Team')
        from_address = f"{sender_name} <{sender_email}>" if sender_name else sender_email

        to_address = f"{to_name} <{to_email}>" if to_name else to_email

        params = {
            "from": from_address,
            "to": [to_email],
            "subject": subject,
        }

        if html_content:
            params["html"] = html_content
            if content:
                params["text"] = content
        else:
            params["text"] = content

        email = resend.Emails.send(params)

        # Log the individual email
        logs = load_json_file('data/logs.json', [])
        log_entry = {
            'school_name': to_name or 'Individual Email',
            'email': to_email,
            'template_used': 'Individual Email',
            'template_id': 0,
            'status': 'Sent',
            'timestamp': datetime.now().isoformat(),
            'email_id': email.get('id', ''),
            'subject': subject
        }
        logs.append(log_entry)
        save_json_file('data/logs.json', logs)

        flash(f'Email sent successfully to {to_email}!', 'success')

    except Exception as e:
        logging.error(f"Error sending individual email: {str(e)}")
        flash(f'Error sending email: {str(e)}', 'error')

    return render_template('individual_email.html')

# Initialize templates on startup
initialize_templates()