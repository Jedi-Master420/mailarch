# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, connection

from mlarchive.archive.thread import process, get_root_set


def clear_threads(apps, schema_editor):
    '''Delete existing threads in preparation for re-compute
    Since Message.thread is actually a mandatory field we
    are setting all Messsages to thread 1 and deleting all 
    the other threads.  This way it will be simple to tell
    which messages, if any, don't get a new thread.
    '''
    Thread = apps.get_model('archive', 'Thread')
    thread = Thread.objects.get(pk=1)
    if Thread.objects.count() > 500000:
        Message.objects.all().update(thread=thread)
        migrations.RunSQL('delete from archive_thread where id > 1')
        #with connection.cursor() as cursor:
        #    cursor.execute('delete from archive_thread where id > 1')
        #    row = cursor.fetchone()


def compute_threads(apps, schema_editor):
    '''Run threading algorithm and populate thread_order,
    thread_depth fields of Message
    '''
    EmailList = apps.get_model("archive", "EmailList")
    Message = apps.get_model("archive", "Message")
    Thread = apps.get_model("archive", "Thread")

    # for elist in EmailList.objects.all().order_by('name'):
    for elist in EmailList.objects.filter(name='cellar'):
        queryset = Message.objects.filter(email_list=elist).order_by('date')
        root_node = process(queryset)
        for branch in get_root_set(root_node):
            if branch.is_empty():
                date = branch.child.message.date
                first = branch.child.message
            else:
                date = branch.message.date
                first = branch.message
            thread = Thread.objects.create(date=date, first=first)
            for container in branch.export():
                if container.is_empty():
                    pass
                else:
                    container.message.thread = thread
                    container.message.thread_order = container.order
                    container.message.thread_depth = container.depth
                    container.message.save()


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0002_auto_20161026_1139'),
    ]

    operations = [
        migrations.RunPython(clear_threads),
        migrations.RunPython(compute_threads),
    ]
