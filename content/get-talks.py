import csv
import lxml.html
import requests

schedule = {}
speakers = {}

with open('schedule.csv', 'w') as csv_out:
    headers = [
        '@type',

        'end',
        'start',

        'title',

        'first_name',
        'last_name',

        'text',
        # 'start', 'end', 'location', 'title', 'level', 'speaker', 'timing'


        'level',
        'timing',

        'path',
        'id',
        'UID',
        'subjects',
        'version',
        'rights',
        'is_folderish',
        'contributors',
        '@components',
        'review_state',
        'expires',
        'effective',
        'language',
        'created',
        'modified',
        'allow_discussion',
        'creators',
        'description',
        'exclude_from_nav',
        'relatedItems',
        'nextPreviousEnabled',
        'open_end',
        'confirm_password',
        'sync_uid',

        'email',
        'bio',
        'password',
        'homepage',
        'whole_day',
        'presenting',
        'event_url',
        'contact_name',
        'recurrence',
        'versioning_enabled',
        'location',
        'contact_phone',
        'contact_email'
                
    ]


    csv_writer = csv.DictWriter(csv_out, headers)
    csv_writer.writeheader()

    for day in [7,8,9]:
        page = requests.get('https://2018.ploneconf.org/schedule/talks-november-%s' % day)
        doc = lxml.html.fromstring(page.content)
        div = doc.get_element_by_id('parent-fieldname-text')
        table = div[1]
        thead = table[0]
        tr = thead[0]

        locations = []
        # Skip the first column
        for td in tr[1:]:
            locations.append(td.text)

        tbody = thead.getnext()
        for tr in tbody:
            th = tr[0]
            row = {n: '' for n in headers}
            row['start'], row['end'] = th.text.split(' - ')
            count = 0
            for td in tr.iter('td'):

                h4 = td.find('h4')
                if h4 is None:
                    h2 = td.find('h2')
                    if h2 is None:
                        # Blank cell
                        continue
                    else:
                        row['title'] = h2.text
                else:
                    row['title'] = h4.text

                row['location'] = locations[count]
                count += 1

                p = td.find('p')
                if p is None:
                    continue
                speakers = []
                if '/' in p.text:
                    speaker, row['level'] = p.text.split(' / ')
                    if speaker.startswith('by '):
                        speaker = speaker[3:]
                    if ',' in speaker:
                        for speaker in speaker.split(' , '):
                            speakers.append(speaker.split(' ', 1))
                    else:
                        speakers.append(speaker.split(' ', 1))
                else:
                    if '(' in p.text:
                        speaker, timing = p.text.split(' (')
                        if speaker.startswith('by '):
                            speaker = speaker[3:]
                        row['timing'] = timing[:-1]
                        speakers.append(speaker.split(' ', 1))


                row['@type'] = 'session'
                csv_writer.writerow(row)

                row['@type'] = 'speaker'
                for speaker in speakers:
                    row['first_name'], row['last_name'] = speaker
                    csv_writer.writerow(row)

                print(row)






