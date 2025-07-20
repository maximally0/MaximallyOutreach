import os
import json
import csv
import io
import logging
import random
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import pandas as pd
import resend

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
        for row in csv_input:
            # Clean and validate row data
            school = {key.strip(): value.strip() for key, value in row.items() if value.strip()}
            if school.get('School Name') and school.get('Email'):
                schools.append(school)
        
        if not schools:
            flash('No valid school records found in CSV. Make sure you have School Name and Email columns.', 'error')
            return redirect(url_for('index'))
        
        # Save schools data
        save_json_file('data/schools.json', schools)
        flash(f'Successfully uploaded {len(schools)} schools', 'success')
        
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
        
        # Replace placeholders
        preview_subject = replace_placeholders(subject, school)
        preview_content = replace_placeholders(content, school)
        
        return jsonify({
            'subject': preview_subject,
            'content': preview_content,
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
        
        schools = load_json_file('data/schools.json', [])
        templates = load_json_file('data/templates.json', [])
        logs = load_json_file('data/logs.json', [])
        
        if not selected_schools:
            return jsonify({'error': 'No schools selected'}), 400
        
        results = []
        
        for school_index in selected_schools:
            if school_index >= len(schools):
                continue
                
            school = schools[school_index]
            
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
            content = custom_content if custom_content else current_template['content']
            
            # Replace placeholders
            email_subject = replace_placeholders(subject, school)
            email_content = replace_placeholders(content, school)
            
            # Send email via Resend
            try:
                params = {
                    "from": "hello@maximally.in",
                    "to": [school['Email']],
                    "subject": email_subject,
                    "text": email_content,
                }
                
                email = resend.Emails.send(params)
                
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
                logging.error(f"Error sending email to {school['Email']}: {str(email_error)}")
                log_entry = {
                    'school_name': school.get('School Name', ''),
                    'email': school['Email'],
                    'template_used': current_template['name'],
                    'template_id': current_template['id'],
                    'status': f'Error: {str(email_error)}',
                    'timestamp': datetime.now().isoformat(),
                    'email_id': '',
                    'subject': email_subject
                }
                
                results.append({'status': 'error', 'school': school['School Name'], 'error': str(email_error)})
            
            logs.append(log_entry)
        
        # Save updated logs
        save_json_file('data/logs.json', logs)
        
        return jsonify({
            'message': f'Email sending completed',
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Error sending emails: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

# Initialize templates on startup
initialize_templates()
