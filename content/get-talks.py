import csv
import lxml.html
import requests
import re

Plone = 'Plone2/'

def slugify(string):
    """
    Slugify a unicode string.
    Example:
        >>> slugify(u"Héllø Wörld")
        u"hello-world"
    """

    return re.sub(r'[-\s]+', '-',
                re.sub(r'[^\w\s-]', '', string)
                .strip().lower())

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

    # Create containers
    containers = [
            ('Conference', 'conference', Plone + 'conference'),
            ('Attendees', 'attendees', Plone + 'conference/attendees'),
            ('Speakers', 'speakers', Plone + 'conference/speakers'),
            ('Locations', 'locations', Plone + 'conference/locations')]
    row = {n: '' for n in headers}
    for container in containers:
        row['title'], row['@type'], row['path'] = container
        row['id'] = container[1]
        csv_writer.writerow(row)

    location_names = set()

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
            locations.append(td.text_content())

        tbody = thead.getnext()
        for tr in tbody:
            th = tr[0]
            row = {n: '' for n in headers}
            row['start'], row['end'] = th.text_content().split(' - ')

            count = 0
            for td in tr.iter('td'):

                location = locations[count]
                count += 1
                if location not in location_names:
                    row['@type'] = 'location'
                    row['title'] = row['location'] = location
                    row['path'] = Plone + 'conference/locations/' + slugify(row['location'])
                    csv_writer.writerow(row)
                    location_names.add(location)

                if td.find('h2'):
                    titles = td.iter('h2')
                else:
                    titles = td.iter('h4')

                if td.find('p'):
                    ps = td.iter('p')
                else:
                    ps = None

                for title in titles:

                    row['@type'] = 'session'
                    row['title'] = title.text_content()
                    print(title.text_content())
                    row['path'] = Plone + 'conference/locations/' + slugify(row['location']) + '/' + slugify(row['title'])
                    csv_writer.writerow(row)

                    if ps:
                        p = next(ps)
                    else:
                        continue

                    speakers = []
                    if '/' in p.text_content():
                        speaker, row['level'] = p.text_content().split(' / ')
                        if speaker.startswith('by '):
                            speaker = speaker[3:]
                        if ',' in speaker:
                            for speaker in speaker.split(' , '):
                                speakers.append(speaker.split(' ', 1))
                        else:
                            speakers.append(speaker.split(' ', 1))
                    else:
                        if '(' in p.text_content():
                            speaker, timing = p.text_content().split(' (')
                            if speaker.startswith('by '):
                                speaker = speaker[3:]
                            row['timing'] = timing[:-1]
                            speakers.append(speaker.split(' ', 1))

                    row['@type'] = 'speaker'
                    for speaker in speakers:
                        row['first_name'], row['last_name'] = speaker
                        fullname = ' '.join([row['first_name'], row['last_name']])
                        row['title'] = fullname
                        row['path'] = Plone + slugify(fullname)
                        csv_writer.writerow(row)

                    # print(row)


