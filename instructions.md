
# CSV Upload Instructions for Maximally Outreach Dashboard

## Required File Format

Your CSV file must be properly formatted with specific column headers for the system to process school data correctly.

## Required Columns

The CSV file **must** contain these exact column headers (case-sensitive):

1. **School Name** - The full name of the educational institution
2. **Email** - The contact email address for outreach
3. **Contact Person** - Name of the person to address emails to
4. **City** - The city where the school is located

## File Format Requirements

- **File Type**: Must be a `.csv` file
- **Encoding**: UTF-8 encoding recommended
- **Headers**: First row must contain the column headers exactly as specified above
- **Required Fields**: `School Name` and `Email` are mandatory - rows without these will be skipped
- **Optional Fields**: `Contact Person` and `City` are optional but recommended for better personalization

## Example CSV Format

```csv
School Name,Email,Contact Person,City
Lincoln Elementary School,principal@lincoln-elem.edu,Sarah Johnson,Springfield
Roosevelt High School,contact@roosevelt-hs.edu,Michael Chen,Riverside
Washington Middle School,admin@washington-ms.edu,Jennifer Davis,Oak Valley
Jefferson Academy,info@jefferson-academy.edu,Robert Martinez,Pine Creek
```

## Data Validation

- Empty rows will be ignored
- Schools without a `School Name` or `Email` will be skipped
- Extra spaces in data will be automatically trimmed
- Additional columns beyond the required ones are allowed but will be ignored

## Email Template Placeholders

Your CSV data will be used to personalize email templates with these placeholders:

- `{{school_name}}` - Replaced with the School Name
- `{{contact_person}}` - Replaced with the Contact Person
- `{{email}}` - Replaced with the Email address
- `{{city}}` - Replaced with the City

## Tips for Best Results

1. **Clean Data**: Ensure email addresses are valid and properly formatted
2. **Complete Information**: Include all optional fields for better personalization
3. **Consistent Formatting**: Use consistent naming conventions for schools
4. **Test Small**: Start with a small CSV file to test the upload process
5. **Backup**: Keep a backup of your original data file

## Common Issues and Solutions

### Upload Errors
- **"No file selected"**: Make sure you've selected a file before clicking upload
- **"Please upload a CSV file"**: Ensure your file has a `.csv` extension
- **"No valid school records found"**: Check that you have the required columns `School Name` and `Email`

### Data Issues
- Missing personalization: Verify that `Contact Person` and `City` columns have data
- Emails not sending: Confirm email addresses are valid and properly formatted

## File Size Limits

- The system can handle CSV files with hundreds of schools
- For very large files (1000+ schools), consider splitting into smaller batches
- Each row should not exceed reasonable text lengths for school names and addresses

## After Upload

Once uploaded successfully:
1. You'll see a confirmation message with the number of schools imported
2. Schools will appear in the dashboard table
3. You can preview emails to verify data was imported correctly
4. Use the template system to send personalized outreach emails

## Need Help?

If you encounter issues with your CSV upload:
1. Check that your file follows the exact format specified above
2. Verify all required columns are present and spelled correctly
3. Ensure your data doesn't have special characters that might cause parsing issues
4. Try uploading a smaller test file first to isolate any problems
