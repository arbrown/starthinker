###########################################################################
#
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

'''
--------------------------------------------------------------

Before running this Airflow module...

  Install StarThinker in cloud composer ( recommended ):

    From Release: pip install starthinker
    From Open Source: pip install git+https://github.com/google/starthinker

  Or push local code to the cloud composer plugins directory ( if pushing local code changes ):

    source install/deploy.sh
    4) Composer Menu
    l) Install All

--------------------------------------------------------------

  If any recipe task has "auth" set to "user" add user credentials:

    1. Ensure an RECIPE['setup']['auth']['user'] = [User Credentials JSON]

  OR

    1. Visit Airflow UI > Admin > Connections.
    2. Add an Entry called "starthinker_user", fill in the following fields. Last step paste JSON from authentication.
      - Conn Type: Google Cloud Platform
      - Project: Get from https://github.com/google/starthinker/blob/master/tutorials/cloud_project.md
      - Keyfile JSON: Get from: https://github.com/google/starthinker/blob/master/tutorials/deploy_commandline.md#optional-setup-user-credentials

--------------------------------------------------------------

  If any recipe task has "auth" set to "service" add service credentials:

    1. Ensure an RECIPE['setup']['auth']['service'] = [Service Credentials JSON]

  OR

    1. Visit Airflow UI > Admin > Connections.
    2. Add an Entry called "starthinker_service", fill in the following fields. Last step paste JSON from authentication.
      - Conn Type: Google Cloud Platform
      - Project: Get from https://github.com/google/starthinker/blob/master/tutorials/cloud_project.md
      - Keyfile JSON: Get from: https://github.com/google/starthinker/blob/master/tutorials/cloud_service.md

--------------------------------------------------------------

CM360 Conversion Upload From Sheets

Move form Sheets to CM.

  - Specify a CM Account ID, Floodligh Activity ID and Conversion Type.
  - Include Sheets url, tab, and range, omit headers in range.
  - Columns: Ordinal, timestampMicros, encryptedUserId | encryptedUserIdCandidates | gclid | mobileDeviceId | matchId | dclid
  - Include encryption information if using encryptedUserId or encryptedUserIdCandidates.

--------------------------------------------------------------

This StarThinker DAG can be extended with any additional tasks from the following sources:
  - https://google.github.io/starthinker/
  - https://github.com/google/starthinker/tree/master/dags

'''

from starthinker.airflow.factory import DAG_Factory

INPUTS = {
  'dcm_account': '',
  'auth_cm': 'user',  # Credentials used for CM.
  'floodlight_activity_id': '',
  'auth_sheets': 'user',  # Credentials to read sheet.
  'floodlight_conversion_type': 'encryptedUserId',  # Must match the values specifed in the last column.
  'encryption_entity_id': '',  # Typically the same as the account id.
  'encryption_entity_type': 'DCM_ACCOUNT',
  'encryption_entity_source': 'DATA_TRANSFER',  # Where the ids are originating from.
  'sheet': 'Name or URL of sheet.',
  'tab': 'Conversions',  # Name of tab within sheet.
  'range': 'A1:E',  # A1 Notation, for example A1:E
}

RECIPE = {
  'tasks': [
    {
      'conversion_upload': {
        'auth': {
          'field': {
            'name': 'auth_cm',
            'kind': 'authentication',
            'order': 1,
            'default': 'user',
            'description': 'Credentials used for CM.'
          }
        },
        'account_id': {
          'field': {
            'name': 'dcm_account',
            'kind': 'string',
            'order': 0,
            'default': ''
          }
        },
        'activity_id': {
          'field': {
            'name': 'floodlight_activity_id',
            'kind': 'integer',
            'order': 1,
            'default': ''
          }
        },
        'conversion_type': {
          'field': {
            'name': 'floodlight_conversion_type',
            'kind': 'choice',
            'order': 2,
            'choices': [
              'encryptedUserId',
              'encryptedUserIdCandidates',
              'dclid',
              'gclid',
              'matchId',
              'mobileDeviceId'
            ],
            'default': 'encryptedUserId',
            'description': 'Must match the values specifed in the last column.'
          }
        },
        'encryptionInfo': {
          'encryptionEntityId': {
            'field': {
              'name': 'encryption_entity_id',
              'kind': 'integer',
              'order': 3,
              'default': '',
              'description': 'Typically the same as the account id.'
            }
          },
          'encryptionEntityType': {
            'field': {
              'name': 'encryption_entity_type',
              'kind': 'choice',
              'order': 4,
              'choices': [
                'ADWORDS_CUSTOMER',
                'DBM_ADVERTISER',
                'DBM_PARTNER',
                'DCM_ACCOUNT',
                'DCM_ADVERTISER',
                'DFP_NETWORK_CODE'
              ],
              'default': 'DCM_ACCOUNT'
            }
          },
          'encryptionSource': {
            'field': {
              'name': 'encryption_entity_source',
              'kind': 'choice',
              'order': 5,
              'choices': [
                'AD_SERVING',
                'DATA_TRANSFER'
              ],
              'default': 'DATA_TRANSFER',
              'description': 'Where the ids are originating from.'
            }
          }
        },
        'from': {
          'sheets': {
            'auth': {
              'field': {
                'name': 'auth_sheets',
                'kind': 'authentication',
                'order': 1,
                'default': 'user',
                'description': 'Credentials to read sheet.'
              }
            },
            'sheet': {
              'field': {
                'name': 'sheet',
                'kind': 'string',
                'order': 9,
                'default': 'Name or URL of sheet.'
              }
            },
            'tab': {
              'field': {
                'name': 'tab',
                'kind': 'string',
                'order': 10,
                'default': 'Conversions',
                'description': 'Name of tab within sheet.'
              }
            },
            'range': {
              'field': {
                'name': 'range',
                'kind': 'string',
                'order': 11,
                'default': 'A1:E',
                'description': 'A1 Notation, for example A1:E'
              }
            }
          }
        }
      }
    }
  ]
}

dag_maker = DAG_Factory('cm360_conversion_upload_from_sheets', RECIPE, INPUTS)
dag = dag_maker.generate()

if __name__ == "__main__":
  dag_maker.print_commandline()
