import csv
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import JsonResponse
from urllib.parse import quote

def file_upload(request):
    if request.method == 'POST':
        try:
            # Extract form data
            owner = request.POST.get('owner')
            industry = request.POST.get('industry')
            skills = request.POST.get('skills')
            systems_methods = request.POST.get('systems-methods')
            ticket_name = request.POST.get('ticket-name')

            # File handling (if any file is uploaded)
            uploaded_files = request.FILES.getlist('files[]')
            file_urls = []  # To store full URLs

            # Handle each uploaded file
            if uploaded_files:
                for file in uploaded_files:
                    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))  # Upload location
                    filename = fs.save(file.name, file)
                    file_url = os.path.join(settings.MEDIA_URL, 'uploads', filename)
                    file_url = file_url.replace('\\', '/')  # Ensure forward slashes in the URL
                    file_url = quote(file_url)  # URL-encode the file URL (e.g., spaces become %20)
                    file_urls.append(request.build_absolute_uri(file_url))  # Build absolute URL

                    # Load the uploaded CSV and process it
                    csv_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

                    # If the uploaded file is CSV, process it
                    if csv_file_path.endswith('.csv'):
                        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile:
                            reader = csv.DictReader(infile)
                            rows = list(reader)

                            # Define the necessary columns
                            required_columns = [
                                'First Name', 'Last Name', 'City/Citta', 'Company Name', 'Job Title',
                                'Linkedin', 'Contact Owner', 'Ticket Owner', 'Ticket Status', 'Pipeline',
                                'Ticket Name', 'Industry', 'Skills', 'Systems & Method'
                            ]

                            # Map the fields
                            field_mapping = {
                                'first_name': 'First Name',
                                'last_name': 'Last Name',
                                'location_name': 'City/Citta',
                                'current_company': 'Company Name',
                                'headline': 'Job Title',
                                'Linkedin': 'Linkedin'
                            }

                            # Get current columns and add missing necessary ones
                            fieldnames = reader.fieldnames if reader.fieldnames else []

                            for col in required_columns:
                                if col not in fieldnames:
                                    fieldnames.append(col)

                            # Update all rows with new form data
                            updated_rows = []
                            for row in rows:
                                for key, mapped_key in field_mapping.items():
                                    if key in row and row[key]:
                                        row[mapped_key] = row[key]

                                # Update necessary fields with form data
                                row['Ticket Name'] = ticket_name
                                row['Industry'] = industry
                                row['Skills'] = skills
                                row['Systems & Method'] = systems_methods
                                row['Contact Owner'] = 'Owner1'  # Always set to 'Owner1'
                                row['Pipeline'] = 'All Jobs'  # Always set to All Jobs
                                row['Ticket Owner'] = 'Owner1'  # Always set to 'Owner1'
                                row['Ticket Status'] = 'Linkedin Message'  # Always set to Linkedin Message

                                # Filter only necessary columns in each row
                                updated_row = {key: row.get(key, '') for key in required_columns}
                                updated_rows.append(updated_row)

                        # Write the updated content to the same CSV file
                        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as outfile:
                            writer = csv.DictWriter(outfile, fieldnames=required_columns)
                            writer.writeheader()
                            writer.writerows(updated_rows)

            # Now, also update the master CSV file in 'media/uploads' for tracking
            master_csv_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'data.csv')
            with open(master_csv_file_path, mode='a', newline='', encoding='utf-8') as master_csvfile:
                master_csv_writer = csv.writer(master_csvfile)
                master_csv_writer.writerow([owner, industry, skills, systems_methods, ticket_name, ', '.join(file_urls)])

            # Return success response with the updated CSV file URL for download
            return JsonResponse({'result': 'success', 'file_url': request.build_absolute_uri(file_url)})

        except Exception as e:
            return JsonResponse({'result': 'error', 'message': str(e)}, status=500)

    return render(request, 'upload_file/upload.html')
