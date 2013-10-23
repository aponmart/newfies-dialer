# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from django.db import connection
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from dialer_campaign.models import Campaign
import logging

logger = logging.getLogger('newfies.filelog')


class SubscriberPerCampaignList(APIView):
    """
    List all subscriber per campaign
    """
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get(self, request, campaign_id=0, contact_id=0, format=None):
        error = {}

        cursor = connection.cursor()
        try:
            Campaign.objects.get(id=campaign_id)
        except:
            error_msg = "Campaign ID does not exists!"
            error['error'] = error_msg
            logger.error(error_msg)
            return Response(error)

        if contact_id and contact_id > 0:
            sql_statement = "SELECT DISTINCT contact_id, last_attempt, "\
                "count_attempt, completion_count_attempt, dialer_subscriber.status,"\
                "dialer_subscriber.id, duplicate_contact "\
                "FROM dialer_subscriber "\
                "LEFT JOIN dialer_callrequest ON "\
                "subscriber_id=dialer_subscriber.id "\
                "LEFT JOIN dialer_campaign ON "\
                "dialer_callrequest.campaign_id=dialer_campaign.id "\
                "WHERE dialer_subscriber.campaign_id = %s "\
                "AND dialer_subscriber.duplicate_contact = '%s'"\
                % (str(campaign_id), str(contact_id))
        else:
            sql_statement = "SELECT DISTINCT contact_id, last_attempt, "\
                "count_attempt, completion_count_attempt, dialer_subscriber.status, "\
                "dialer_subscriber.id, duplicate_contact "\
                "FROM dialer_subscriber "\
                "LEFT JOIN dialer_callrequest ON "\
                "subscriber_id="\
                "dialer_subscriber.id "\
                "LEFT JOIN dialer_campaign ON "\
                "dialer_callrequest.campaign_id=dialer_campaign.id "\
                "WHERE dialer_subscriber.campaign_id"\
                "= %s" % (str(campaign_id))

        cursor.execute(sql_statement)
        row = cursor.fetchall()

        result = []
        for record in row:
            modrecord = {}
            modrecord['contact_id'] = record[0]
            modrecord['last_attempt'] = record[1]
            modrecord['count_attempt'] = record[2]
            modrecord['completion_count_attempt'] = record[3]
            modrecord['status'] = record[3]
            modrecord['subscriber_id'] = record[4]
            modrecord['contact'] = record[6]
            result.append(modrecord)

        return Response(result)