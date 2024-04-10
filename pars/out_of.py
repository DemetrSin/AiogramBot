# def main(self):
#     html_content = self.fetch_job_listings()
#     if html_content:
#         job_listings = self.parse_job_listings(html_content)
#         filtered_listings = self.filter_listings(job_listings)
#         with (open('data1.txt', 'r', encoding='utf-8') as file_read,
#               open('data2.txt', 'a', encoding='utf-8') as file_append):
#             data = file_read.read()
#             for job, href in filtered_listings.items():
#                 if str(href) not in data:
#                     file_append.write(job + ' : ' + str(href) + '\n'*2)

