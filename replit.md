# Maximally Outreach Dashboard

## Overview

This is a Flask-based web application designed for educational outreach campaigns. The system allows users to upload school data, manage email templates, and send personalized outreach emails to educational institutions. It features template management, A/B testing capabilities, and email tracking functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: Traditional server-side rendered HTML with Bootstrap CSS framework
- **Styling**: Bootstrap with dark theme and Bootstrap Icons
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Templates**: Jinja2 templating engine for dynamic content rendering

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Monolithic application with single `app.py` file
- **Session Management**: Flask's built-in session handling with secret key
- **Entry Point**: `main.py` serves as the application runner

### Data Storage Solutions
- **Primary Storage**: JSON files for persistent data storage
- **File Structure**:
  - `data/schools.json` - School contact information
  - `data/templates.json` - Email templates with placeholders
  - `data/logs.json` - Email sending activity logs
- **File Uploads**: CSV processing for bulk school data import

### Authentication and Authorization
- **Current State**: No authentication system implemented
- **Session Security**: Basic session secret key configuration
- **Access Control**: Open access to all functionality

## Key Components

### Data Management
- **School Data**: CSV upload and JSON storage system for school information (name, email, contact person, city)
- **Template System**: Pre-defined email templates with variable placeholders ({{school_name}}, {{contact_person}}, {{city}})
- **Logging**: Activity tracking for sent emails and system events

### Email System
- **Provider**: Resend API integration for email delivery
- **Features**: Template-based personalized emails with variable substitution
- **A/B Testing**: Support for testing multiple templates simultaneously

### User Interface
- **Dashboard**: Single-page interface with multiple functional sections
- **File Upload**: CSV import functionality for bulk school data
- **Template Management**: Interface for selecting and managing email templates
- **Bulk Operations**: Select all/individual school targeting options

## Data Flow

1. **Data Import**: Users upload CSV files containing school information
2. **Template Selection**: Users choose from pre-defined email templates or enable A/B testing
3. **Target Selection**: Users select specific schools or all schools for outreach
4. **Email Processing**: System personalizes templates with school-specific data
5. **Email Delivery**: Resend API handles email transmission
6. **Activity Logging**: System records email sending activities and results

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **Pandas**: CSV data processing and manipulation
- **Resend**: Email delivery service integration

### Frontend Dependencies
- **Bootstrap CSS**: UI framework with dark theme
- **Bootstrap Icons**: Icon library for user interface elements

### Environment Variables
- **RESEND_API_KEY**: Email service authentication
- **SESSION_SECRET**: Flask session security key

## Deployment Strategy

### Current Configuration
- **Development**: Flask development server on port 5000
- **Host Binding**: Configured for 0.0.0.0 (all interfaces)
- **Debug Mode**: Enabled for development environment

### File System Requirements
- **Data Directory**: Auto-created 'data' folder for JSON storage
- **Template Initialization**: Automatic creation of default email templates
- **Error Handling**: JSON file loading with fallback mechanisms

### Environment Setup
- **Python Environment**: Requires Flask, Pandas, and Resend libraries
- **File Permissions**: Write access needed for data directory
- **API Configuration**: Resend API key must be configured for email functionality

The application is designed as a simple, self-contained system suitable for small to medium-scale educational outreach campaigns, with room for future enhancements like user authentication, database integration, and advanced analytics.