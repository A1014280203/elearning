# # 1014280203-buyer@qq.com
# # 1014280203-facilitator@qq.com
# from requests import auth
# import requests
#
# # CLIENT_ID = 'AVf33zW-AgGVKImdGJ239IsEcYoZUpP2hD6cwr9-Q1Epn3No9Y2zzOB5cQcy3uZDK0bD8okEGJou6--Y'
# # SECRET = 'EP3rNqCw52FbYsU_Ev6HIUSYItbD3MLRPfbPbFPYsWxFbPWiwClsmpi8Kl2w0jr7NtpW9QzDOjPRK6La'
# #
# #
# # ACCESS_TOKEN = 'https://api.sandbox.paypal.com/v1/oauth2/token'
# #
# # payload = {'grant_type': 'client_credentials'}
# # auth.HTTPBasicAuth(CLIENT_ID, SECRET)
# #
# # resp = requests.post(ACCESS_TOKEN, data=payload, auth=auth.HTTPBasicAuth(CLIENT_ID, SECRET))
# # print(resp.request.headers)
# # print(resp.status_code)
# # print(resp.text)
#
# # TRANSACTION = 'https://api.sandbox.paypal.com/v1/payments/payment'
# #
# TOKEN_RESPONSE = {
#     "scope": "https://uri.paypal.com/services/subscriptions "
#              "https://api.paypal.com/v1/payments/.* "
#              "https://api.paypal.com/v1/vault/credit-card "
#              "https://uri.paypal.com/services/applications/webhooks "
#              "openid https://uri.paypal.com/payments/payouts "
#              "https://api.paypal.com/v1/vault/credit-card/.*",
#     "nonce": "2017-08-24T02:48:14Z1jWNWxMi_5eikSA5UTwSS1unmTUduEHdB2JnWr-sBsU",
#     "access_token": "A21AAHV1OO6rOW4mXZx7zAKG13FCN4y6vvQ0fuVdS6Ro2edV4j73uxNlwhYaM_QqqLpfH9BEjpzBnt9ix83D6nXQtLC9J91BA",
#     "token_type": "Bearer",
#     "app_id": "APP-80W284485P519543T",
#     "expires_in": 32400
# }
# #
# # add_headers = {
# #     "Content-Type": "application/json",
# #     "Authorization": "Bearer " + TOKEN_RESPONSE['access_token']
# # }
# #
# # payload = {
# #   "intent": "sale",
# #   "redirect_urls": {
# #     "return_url": "http://example.com/your_redirect_url.html",
# #     "cancel_url": "http://example.com/your_cancel_url.html"
# #   },
# #   "payer": {
# #     "payment_method": "paypal"
# #   },
# #   "transactions": [{
# #     "amount": {
# #       "total": "7.47",
# #       "currency": "USD"
# #     }
# #   }]
# # }
# #
# # resp = requests.post(TRANSACTION, json=payload, headers=add_headers)
# # print(resp.request.headers)
# # print(resp.status_code)
# # print(resp.text)
# #
# # TRAN_RESP = {
# #     "id": "PAY-3A767039T05672047LGPEDBA",
# #     "intent": "sale",
# #     "state": "created",
# #     "payer": {"payment_method": "paypal"},
# #     "transactions": [
# #         {
# #             "amount":
# #                 {
# #                     "total": "7.47",
# #                     "currency": "USD"
# #                 },
# #             "related_resources": []
# #         }
# #     ],
# #     "create_time": "2017-08-24T03:01:24Z",
# #     "links": [
# #         {
# #             "href": "https://api.sandbox.paypal.com/v1/payments/payment/PAY-3A767039T05672047LGPEDBA",
# #             "rel": "self",
# #             "method": "GET"
# #         },
# #         {
# #             "href": "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=EC-3UW41011EF659813E",
# #             "rel": "approval_url",
# #             "method": "REDIRECT"
# #         },
# #         {"href": "https://api.sandbox.paypal.com/v1/payments/payment/PAY-3A767039T05672047LGPEDBA/execute",
# #          "rel": "execute",
# #          "method": "POST"
# #          }
# #     ]
# # }
#
# # add_headers = {
# #     "Content-Type": "application/json",
# #     "Authorization": "Bearer " + TOKEN_RESPONSE['access_token']
# # }
# #
# # exec_data = {
# #     'payer_id': 'E8RC56X9A9XHL',
# #     # 'paymentID': 'PAY-3A767039T05672047LGPEDBA'
# # }
# #
# # EXECUTE = "https://api.sandbox.paypal.com/v1/payments/payment/PAY-3A767039T05672047LGPEDBA/execute/"
# #
# # resp = requests.post(EXECUTE, headers=add_headers, json=exec_data)
# # print(resp.request.headers)
# # print(resp.status_code)
# # print(resp.text)
# #
# # EXEC_RESPONSE = {
# #     "id":"PAY-3A767039T05672047LGPEDBA",
# #     "intent":"sale",
# #     "state":"approved",
# #     "cart":"3UW41011EF659813E",
# #     "payer":{"payment_method":"paypal",
# #              "status":"VERIFIED",
# #              "payer_info":{"email":"1014280203-buyer@qq.com",
# #                            "first_name":"test",
# #                            "last_name":"buyer",
# #                            "payer_id":"E8RC56X9A9XHL",
# #                            "shipping_address":
# #                                {"recipient_name":"test buyer",
# #                                 "line1":"NO 1 Nan Jin Road",
# #                                 "city":"Shanghai",
# #                                 "state":"Shanghai",
# #                                 "postal_code":"200000",
# #                                 "country_code":"C2"},
# #                            "country_code":"C2"}},
# #     "transactions":[{"amount":{"total":"7.47",
# #                                "currency":"USD",
# #                                "details":{}},
# #                      "payee":{"merchant_id":"DP2PYNK665V7S",
# #                               "email":"1014280203-facilitator@qq.com"},
# #                      "item_list":{"shipping_address":{"recipient_name":"buyer test",
# #                                                       "line1":"NO 1 Nan Jin Road",
# #                                                       "city":"Shanghai",
# #                                                       "state":"Shanghai",
# #                                                       "postal_code":"200000",
# #                                                       "country_code":"C2"}},
# #                      "related_resources":[{"sale":{"id":"7BX456892F1742329",
# #                                                    "state":"pending",
# #                                                    "amount":{"total":"7.47",
# #                                                              "currency":"USD",
# #                                                              "details":{"subtotal":"7.47"}},
# #                                                    "payment_mode":"INSTANT_TRANSFER",
# #                                                    "reason_code":"PAYMENT_REVIEW",
# #                                                    "protection_eligibility":"INELIGIBLE",
# #                                                    "transaction_fee":{"value":"0.55",
# #                                                                       "currency":"USD"},
# #                                                    "parent_payment":"PAY-3A767039T05672047LGPEDBA",
# #                                                    "create_time":"2017-08-24T04:14:12Z",
# #                                                    "update_time":"2017-08-24T04:14:12Z",
# #                                                    "links":[{"href":"https://api.sandbox.paypal.com/v1/payments/sale/7BX456892F1742329",
# #                                                              "rel":"self",
# #                                                              "method":"GET"},
# #                                                             {"href":"https://api.sandbox.paypal.com/v1/payments/sale/7BX456892F1742329/refund",
# #                                                              "rel":"refund",
# #                                                              "method":"POST"},
# #                                                             {"href":"https://api.sandbox.paypal.com/v1/payments/payment/PAY-3A767039T05672047LGPEDBA",
# #                                                              "rel":"parent_payment",
# #                                                              "method":"GET"}]}}]}],
# #     "create_time":"2017-08-24T04:14:12Z",
# #     "links":[{"href":"https://api.sandbox.paypal.com/v1/payments/payment/PAY-3A767039T05672047LGPEDBA",
# #               "rel":"self",
# #               "method":"GET"}]}

# from requests import session

# s1 = session()
# s1.post('http://localhost:5000/login',data={'email': 'user@email.com', 'password':'12345678'})
# s1.post('http://localhost:5000/person/message',json={'m_cont': 'message#1', 'm_to':1})
# s2 = session()
# s2.post('http://localhost:5000/login',data={'email': 'teacher@email.com', 'password':'12345678'})
# s2.post('http://localhost:5000/person/message',json={'m_cont': 'message#2', 'm_to':1})
# s3 = session()
# s3.post('http://localhost:5000/login',data={'email': 'benjamin@mita.mil', 'password':'12345678'})
# r2 = s3.get('http://localhost:5000/person/message')
# print(r2.text)
# print('*'*20)
# r3 = s3.get('http://localhost:5000/person/message/22')
# print(r3.text)

# angela@bubblemix.edu
# rebecca@topiclounge.net
# from requests import session
#
# s0 = session()
# s0.post('http://localhost:5000/login', data={'email': 'angela@bubblemix.edu', 'password': '12345678'})
# resp = s0.get('http://localhost:5000/person/child')
# print(resp.text)
# print('---bind now---')
# s1 = session()
# s1.post('http://localhost:5000/login', data={'email': 'rebecca@topiclounge.net', 'password': '12345678'})
# s1.post('http://localhost:5000/person/parent', data={'u_email': 'angela@bubblemix.edu'})
# print('--------------')
# resp = s0.get('http://localhost:5000/person/child')
# print(resp.text)