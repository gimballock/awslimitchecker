"""
awslimitchecker/tests/support.py

The latest version of this package is available at:
<https://github.com/jantman/awslimitchecker>

################################################################################
Copyright 2015 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of awslimitchecker, also known as awslimitchecker.

    awslimitchecker is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    awslimitchecker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with awslimitchecker.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/awslimitchecker> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

from awslimitchecker.limit import AwsLimit
import logging
import sys

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import Mock
else:
    from unittest.mock import Mock


class LogRecordHelper(object):
    """class to help working with an array of LogRecords"""

    levelmap = {
        logging.CRITICAL: 'critical',
        logging.ERROR: 'error',
        logging.WARNING: 'warning',
        logging.INFO: 'info',
        logging.DEBUG: 'debug',
        logging.NOTSET: 'notset'
    }

    def __init__(self, logcapture):
        """
        Initialize LogRecord helper.

        :param logcapture: testfixtures.logcapture.LogCapture object
        """
        self._logcapture = logcapture
        self.records = logcapture.records

    def get_at_level(self, lvl):
        """
        Return a list of all records in order for a given numeric logging level

        :param lvl: the level to get
        :type lvl: int
        :returns: list of LogRecord objects
        """
        res = []
        for rec in self.records:
            if rec.levelno == lvl:
                res.append(rec)
        return res

    def get_at_or_above_level(self, lvl):
        """
        Return a list of all records in order, at OR ABOVE a given numeric
        logging level

        :param lvl: the level to get
        :type lvl: int
        :returns: list of LogRecord objects
        """
        res = []
        for rec in self.records:
            if rec.levelno >= lvl:
                res.append(rec)
        return res

    def assert_failed_message(self, records):
        """
        Return a list of string representations of the log records, for use
        in assertion failure messages.

        :param records: list of LogRecord objects
        :return: list of strings
        """
        res = ""
        for r in records:
            res += '%s:%s.%s (%s:%s) %s - %s %s\n' % (
                r.name,
                r.module,
                r.funcName,
                r.filename,
                r.lineno,
                r.levelname,
                r.msg,
                r.args
            )
        return res

    def unexpected_logs(self, allow_endpoint_error=False):
        """
        Return a list of strings representing awslimitchecker log messages
        in this object's log records, that shouldn't be encountered in normal
        operation.

        :param allow_endpoint_error: if true, will ignore any WARN messages
          containing 'Could not connect to the endpoint URL:' in their first
          argument
        :type allow_endpoint_error: bool
        :return: list of strings representing log records
        """
        res = []
        msg = 'Cannot check TrustedAdvisor: %s'
        args = ('AWS Premium Support Subscription is required to use this '
                'service.', )
        for r in self.get_at_or_above_level(logging.WARN):
            if (r.levelno == logging.WARN and r.module == 'trustedadvisor' and
                    r.funcName == '_get_limit_check_id' and r.msg == msg and
                    r.args == args):
                continue
            if (allow_endpoint_error and r.levelno == logging.WARN and
                    len(r.args) > 0 and
                    'Could not connect to the endpoint URL:' in r.args[0]):
                continue
            res.append('%s:%s.%s (%s:%s) %s - %s %s' % (
                r.name,
                r.module,
                r.funcName,
                r.filename,
                r.lineno,
                r.levelname,
                r.msg,
                r.args
            ))
        return res

    @property
    def num_ta_polls(self):
        """
        Return the number of times Trusted Advisor polled.

        :return: number of times Trusted Advisor polled
        :rtype: int
        """
        count = 0
        for r in self.records:
            if 'Beginning TrustedAdvisor poll' in r.msg:
                count += 1
        return count


def sample_limits():
    limits = {
        'SvcBar': {
            'barlimit1': AwsLimit(
                'barlimit1',
                'SvcBar',
                1,
                2,
                3,
                limit_type='ltbar1',
                limit_subtype='sltbar1',
            ),
            'bar limit2': AwsLimit(
                'bar limit2',
                'SvcBar',
                2,
                2,
                3,
                limit_type='ltbar2',
                limit_subtype='sltbar2',
            ),
        },
        'SvcFoo': {
            'foo limit3': AwsLimit(
                'foo limit3',
                'SvcFoo',
                3,
                2,
                3,
                limit_type='ltfoo3',
                limit_subtype='sltfoo3',
            ),
        },
    }
    limits['SvcBar']['bar limit2'].set_limit_override(99)
    limits['SvcFoo']['foo limit3']._set_ta_limit(10)
    return limits


def sample_limits_api():
    limits = {
        'SvcBar': {
            'barlimit1': AwsLimit(
                'barlimit1',
                'SvcBar',
                1,
                2,
                3,
                limit_type='ltbar1',
                limit_subtype='sltbar1',
            ),
            'bar limit2': AwsLimit(
                'bar limit2',
                'SvcBar',
                2,
                2,
                3,
                limit_type='ltbar2',
                limit_subtype='sltbar2',
            ),
        },
        'SvcFoo': {
            'foo limit3': AwsLimit(
                'foo limit3',
                'SvcFoo',
                3,
                2,
                3,
                limit_type='ltfoo3',
                limit_subtype='sltfoo3',
            ),
            'zzz limit4': AwsLimit(
                'zzz limit4',
                'SvcFoo',
                4,
                1,
                5,
                limit_type='ltfoo4',
                limit_subtype='sltfoo4',
            ),
        },
    }
    limits['SvcBar']['bar limit2']._set_api_limit(2)
    limits['SvcBar']['bar limit2'].set_limit_override(99)
    limits['SvcFoo']['foo limit3']._set_ta_limit(10)
    limits['SvcFoo']['zzz limit4']._set_api_limit(34)
    return limits


class RetryTests(object):

    """
    {'cookies': <RequestsCookieJar[]>, '_content': '<?xml version="1.0" encoding="UTF-8"?>\n<DescribeVpcsResponse xmlns="http://ec2.amazonaws.com/doc/2015-10-01/">\n    <requestId>5b9f8b96-4e09-4651-a578-0dbca7d79946</requestId>\n    <vpcSet>\n        <item>\n            <vpcId>vpc-47807c22</vpcId>\n            <state>available</state>\n            <cidrBlock>172.31.0.0/16</cidrBlock>\n            <dhcpOptionsId>dopt-3c4e535e</dhcpOptionsId>\n            <instanceTenancy>default</instanceTenancy>\n            <isDefault>true</isDefault>\n        </item>\n    </vpcSet>\n</DescribeVpcsResponse>', 'headers': {'transfer-encoding': 'chunked', 'vary': 'Accept-Encoding', 'server': 'AmazonEC2', 'content-type': 'text/xml;charset=UTF-8', 'date': 'Sat, 21 May 2016 02:22:53 GMT'}, 'url': u'https://ec2.us-west-2.amazonaws.com/', 'status_code': 200, '_content_consumed': True, 'encoding': 'UTF-8', 'request': <PreparedRequest [POST]>, 'connection': <botocore.vendored.requests.adapters.HTTPAdapter object at 0x7efe8c8bac50>, 'elapsed': datetime.timedelta(0, 0, 684463), 'raw': <botocore.vendored.requests.packages.urllib3.response.HTTPResponse object at 0x7efe8c862d50>, 'reason': 'OK', 'history': []}
    """
    describe_vpcs_1 = Mock()
    type(describe_vpcs_1).content = '<?xml version="1.0" encoding="UTF-8"?>\n<DescribeVpcsResponse xmlns="http://ec2.amazonaws.com/doc/2015-10-01/">\n    <requestId>5b9f8b96-4e09-4651-a578-0dbca7d79946</requestId>\n    <vpcSet>\n        <item>\n            <vpcId>vpc-47807c22</vpcId>\n            <state>available</state>\n            <cidrBlock>172.31.0.0/16</cidrBlock>\n            <dhcpOptionsId>dopt-3c4e535e</dhcpOptionsId>\n            <instanceTenancy>default</instanceTenancy>\n            <isDefault>true</isDefault>\n        </item>\n    </vpcSet>\n</DescribeVpcsResponse>'
    type(describe_vpcs_1).headers = {'transfer-encoding': 'chunked', 'vary': 'Accept-Encoding', 'server': 'AmazonEC2', 'content-type': 'text/xml;charset=UTF-8', 'date': 'Sat, 21 May 2016 02:22:53 GMT'}
    type(describe_vpcs_1).status_code = 200

    describe_vpcs_rate_limit = Mock()
    type(describe_vpcs_rate_limit).content = '<?xml version="1.0" encoding="UTF-8"?>\n<Response><Errors><Error><Code>RequestLimitExceeded</Code><Message>Request limit exceeded.</Message></Error></Errors><RequestID>44c0f570-e338-48dd-9953-6684fa586dcb</RequestID></Response>'
    type(describe_vpcs_rate_limit).headers = {'transfer-encoding': 'chunked', 'date': 'Sat, 21 May 2016 11:08:53 GMT', 'server': 'AmazonEC2'}
    type(describe_vpcs_rate_limit).status_code = 400

    describe_vpcs_throttling = Mock()
    type(describe_vpcs_throttling).content = '<?xml version="1.0" encoding="UTF-8"?>\n<Response><Errors><Error><Type>Sender</Type><Code>Throttling</Code><Message>Rate exceeded</Message></Error></Errors><RequestID>44c0f570-e338-48dd-9953-6684fa586dcb</RequestID></Response>'
    type(describe_vpcs_throttling).headers = {'transfer-encoding': 'chunked', 'date': 'Sat, 21 May 2016 11:08:53 GMT', 'server': 'AmazonEC2'}
    type(describe_vpcs_throttling).status_code = 400
