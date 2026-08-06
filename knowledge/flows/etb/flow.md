# ETB_NEW Flow Knowledge

This file is generated from the canonical Visio source. Do not edit manually.

- Source Visio: `docs/source/sequence-diagrams/etb/current/Onboarding_Sequence Diagram.vsdx`
- Synchronization date: `2026-08-05`
- Generation timestamp: `2026-08-06T04:03:13Z`

## Business Purpose

Canonical ETB_NEW business sequence represented by the Visio pages: ETB(MVP0); ETB(MMP Lot1); ETB(MMP Lot2); ETB(Post-MMP1); ETB (FR & MVP0); ETB(MMP Lot1)_CDP; ETB(MMP Lot2)_CDP; ETB_Host (MMP Lot2); ETB_Host (FR); ETB (MVP0) Backup; ETB (MMP)_Backup; ETB(MMP Lot2)_Backup; ETB (FR)_Backup; ETB (Full)Backup; ETB_Ping; ETB (MVP0) Back up 19 Aug

## Expected Sequence

### Page 1: ETB(MVP0)

1. 1. First Page
2. 2. Welcome Page
3. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
4. Defer to MVP2 Face Liveness check (SDK)
5. Apigee (Engagement)
6. Apigee (Experience)
7. CIAM (SAAS – no SecureConnect)
8. IAM Proxy (Experience)
9. CIAM (SaaS)
10. Ask Permission for -Activity tracking -Push notification
11. 3. Accept T&C
12. T&C-MS/DB
13. Auth_ID token (10minutes expired)
14. 4. Input ID & DOB
15. TBC -Combine services
16. 5. Input Laser code
17. (Restful/XML)
18. 6. Display Mobile No.
19. User input phone number, no check sim
20. 7. Input OTP
21. 8. Consent PDPA
22. TBC
23. PDPA content/DB
24. 9. Introduction for face scan
25. Ask Permission for -Camera
26. 10. Face scan
27. Cache PPI data on redis: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime
28. FR – No Liveness SDK, only capture face photo send to compare at backend system
29. If CIS = Success then start process in Camunda otherwise send failure message.
30. 11. Set up PIN and Reconfirm PIN
31. Create Customer Prospect Profile Record Create RegistrationRecord
32. Update Customer Prospect Profile Record
33. JWT Token (CIS ID)
34. CIS ID
35. If API update CustomerProfileRelAdd fail
36. Check if duplicate mobile no. in CIS Profile
37. If found duplicate mobile no.
38. Delete duplicate mobile no.
39. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
40. OPO get EntraID (Virtual ID)
41. Retry 3 times
42. 12. Select Product
43. Cache
44. 13.Suceess
45. Update RegistrationRecord
46. Control Screen
47. OPO_02: Get Customer Account /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id Request: - Response: products
48. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
49. IAM proxy (Experience)
50. APIGee (Experience)
51. APIGee (Engagement)
52. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
53. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
54. API#3: /cis/v1/customers-accounts/inquiry/account
55. API#1: /opo/onboarding/customers/v1/etb/products
56. OPO_03: Add Account to CIS OPO API detail - POST /opo/onboarding/customers/v1/etb/registration Request: products Response: Success/Failure
57. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/onboarding/customers/v1/etb/registration Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
58. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
59. OPO_04 OPO API detail – POST /opo/onboarding/customers/v1/etb Request: Same as OPO_01
60. OPO_07 OPO detail – POST /opo/onboarding/customers/v1/etb Request: Same as OPO_03
61. E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
62. CIS_11: Get Customer Profile Request: CIS ID Response: cisId, partyCertificateType (idType), identifierType (RMNO, EXTID), identifierTypeValue, partyPrefix, partyFirstName, partyLastname, partyPrefixEn, partyFirstNameEn, partyLastNameEN, partyFullNameEn, partydisplayName, dob, partyBlockedStatus, classificationType, classificationTypevalue, partyChannelStatus, partyChannelBlock
63. E6: Publish Event Event topic: <env>.cis.update.customer.success EventType: ADD_ACCOUNT
64. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
65. E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
66. CIS ID and Registration Process Instance Key
67. E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
68. Liveness Check If it passes, proceed the Face comparison
69. Generate Key call to CIAM
70. Store DigitalID & DeviceBindingKey
71. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
72. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
73. E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
74. Fetch Task
75. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
76. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
77. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
78. API#2: /opo/onboarding/customers/v1/etb/products
79. OPO_05 OPO detail – Start Process, submit task vai gRPC
80. OPO_06: Get Customer Account /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id, bbl-cust-id-token Request: - Response: products
81. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
82. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
83. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
84. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
85. auth ID token – return in every call, change to the new one every call (60 minutes expired)
86. auth ID token in the request
87. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
88. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
89. Get PDPA content (TBD) Request: ??? Response: ???
90. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
91. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
92. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
93. IAM_16: OPO 01
94. Get T&C content (TBD) Request: ??? Response: SessionID, ???
95. CIAM validates OTP. If it matches, then can proceed further
96. If users already accepted PDPA clause 6, skip to Face verificatoin
97. CIAM checks bblscore. If it equals to 3, then can proceed further
98. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
99. Submit device meta data Request: metadata, location, message Response: T&C URL
100. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
101. System token issued by Ping
102. Review Security with SM if need to go through Apigee Engagement (ADR_15)
103. CIAM checks 1. ctCode = 09 (To-be: check ctCode & idType in MMP) 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
104. CIAM checks ID card expired date, allow to continue if expired date is today
105. Private API - Group System token issued by Camunda
106. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
107. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
108. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
109. IAM_03: Customer Profile Inquiry (To-be: IAM_13) Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
110. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
111. IAM_11: Update PDPA consent (To-be: IAM_18)
112. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
113. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
114. IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
115. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
116. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
117. IAM_08: Send SMS OTP Request: mobileNum Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
118. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
119. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
120. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
121. CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
122. CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
123. CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
124. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
125. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
126. CIS_08: Get Customer Account Relationship /cis/v1/customers-accounts/inquiry/account Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
127. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
128. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
129. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
130. CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
131. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
132. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
133. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
134. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
135. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
136. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
137. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
138. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
139. If CIS returned errors for update PDPA, then end the flow.
140. If CIS profile not found or CIS status is invalid, search RM
141. If RM is found, get customer profile from RM
142. If cache not found, then inquiry C2A from RM.
143. If RM is found, get customer account relationship from RM
144. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
145. H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
146. CIAM token in the API request (1st call)

### Page 2: ETB(MMP Lot1)

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. CIAM (SAAS – no SecureConnect)
4. Apigee (Experience)
5. IAM Proxy (Experience)
6. Apigee (Engagement)
7. 0A.Splash
8. 1. First Page
9. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
10. Defer to MVP2 Face Liveness check (SDK)
11. CIAM (SaaS)
12. 2. Welcome Page
13. Ask Permission for -Activity tracking -Push notification
14. 3. Accept T&C
15. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
16. Auth ID token in the request
17. Auth_ID token (10minutes expired)
18. V1 - CIS_01: Customer Search by Citizen ID POST: /cis/v1/customer-onboarding/inquiry/profile Request: idNum Response: DoB, RM No. or CIS No., CIS status V2 - CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
19. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
20. StartProcessByCID Request: citizen ID, DOB, idType, MobileNo Response: citizen ID, DOB, prompt laserCode
21. IAM_02: Customer Search Request: idNum, idType Response: cisId, cisIdStatus, channel, rmNum, dob
22. 4. Input ID & DOB & Mobile No
23. If CIS profile not found or CIS status is invalid, search RM
24. - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
25. MMP Scope include CI, PP (CT 11, 52) only
26. V1 - CIS_02: Customer Profile Inquiry (for SAAS) POST: /cis/v1/customer-onboarding/inquiry/profile/accounts Request: RM No. Response: CT, KYC risk level, KYC risk reason code, BBLIAL, Flag Has Active Accounts V2 - CIS_Wrapper (2): Get customer Profile POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: rmNum, {customerProfileBan} Response: RM No., ctCode, gender, customerStatus, nationality, firstName, lastName, type, riskLevel, riskReason, bblIalCode, idpIalCode
27. If RM is found, get customer profile from RM
28. [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
29. H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
30. IAM_26 (new): Get Customer Profile (MB Profile & RM Profile) Request: IdType, idNum, ProfileOption Response: riskLevel, riskLevelReasonCode, bblIalCode, firstName, lastName, Mobile, profileStatus, channelStatus, ctCode, CI & PP & KYC expiryDate
31. [CIAM checks] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_04 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
32. [CIAM checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
33. V1 - CIS_04: Get Customer Mobile Numbers POST: /cis/v1/customer-onboarding/inquiry/mobile Request: RM No. Response: mobileNumberList (90-97, 99) V2 - CIS_Wrapper (4): Customer Mobile Numbers POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: RM No., {customerMobileNumber} Response: contactNum, contactType, seqNum
34. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
35. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
36. V1 - CIS_03: Get Customer ID Card Info POST: /cis/v1/customer-onboarding/inquiry/identity Request: CitizenID Response: ID expiry date, First name, Last name, Title V2 - CIS_Wrapper (3): Get Customer ID Card Info POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: CitizenID,photFlag, tellerId, dailyFlag, dataTypeFlag, {customerIdentity} Response: ID expiry date, First name, Last name, Title
37. [CIAM checks] If customer idType = CI, Continue to IAM_04 Else, Skip IAM_04 and IAM05 Continue at IAM_06 IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
38. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
39. 5. Verification Options
40. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
41. Continue to ETB with MB Flow
42. [CIAM checks] ID card expired date, allow to continue if expired date is today
43. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description Remark: (Restful/XML)
44. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
45. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
46. Review Security with SM if need to go through Apigee Engagement (ADR_15)
47. 6. Input Laser code
48. [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
49. [CIAM checks] result: contains only “dateTime” and no “suspiciousCustomerInfo” Then, can proceed further
50. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
51. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
52. IAM_08: Send SMS OTP Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
53. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
54. *Send OTP with Mobile No.in CIAM cache from Step 4 (TBC where to keep Mobile No. in CIAM)
55. 7. Input OTP
56. 8. Consent PDPA
57. 9. Introduction for face scan
58. Ask Permission for -Camera
59. 10. Face scan
60. FR – No Liveness SDK, only capture face photo send to compare at backend system
61. Cache PPI data on redis: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime
62. 11. Set up PIN and Reconfirm PIN
63. Create RegistrationRecord
64. Create Customer Prospect Profile Record
65. Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
66. Check duplicate mobile no. and email in existing CIS Profile
67. If found duplicate mobile no.
68. Delete duplicate mobile no.
69. If CIS = Success then start process in Camunda otherwise send failure message.
70. CIS ID
71. JWT Token
72. Process daily batch
73. ATM Mgmt.
74. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
75. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
76. Update Customer Prospect Profile Record
77. Terminate Stale Processes
78. OPO get EntraID (Virtual ID)
79. Retry 3 times
80. 12. Select Product
81. Read the Cache for the Product details
82. TBC: Solution for checking Account owner in RM match with Account owner in ST
83. Validate account no. with RM relationship
84. 13.Suceess
85. Control Screen
86. Update RegistrationRecord
87. CNH
88. APIGee (Experience)
89. IAM proxy (Experience)
90. APIGee (Engagement)
91. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
92. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType != ‘CI’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Remark: If Fail to Create TSP Profile, OPO will not retry
93. V1 - CIS_08: Get Customer Account Relationship POST: /cis/v1/customers-accounts/inquiry/account Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship) V2 - CIS_Wrapper (8): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
94. OPO_02: Get Customer Account /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id Request: - Response: products
95. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
96. Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
97. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
98. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
99. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
100. V1 - CIS_05: PDPA Consent Inquiry (Clause 6) POST: /cis/v1/customer-onboarding/core/pdpa Request: ID, ID Type Response: Purpose Code, Purpose Flag (for clause 6 only) V2 - CIS_Wrapper (5): PDPA Consent Inquiry POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: ID, ID Type, {pdpa} Response: Purpose Code, Purpose Flag (all clause)
101. Submit device meta data Request: metadata, location, message Response: T&C URL
102. API#1: /opo/onboarding/customers/v1/etb/products
103. OPO_03: Add Account to CIS OPO API detail - POST /opo/onboarding/customers/v1/etb/registration Request: products Response: Success/Failure
104. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: cis_id,externalId, processInstanceKey
105. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
106. OPO_04 OPO API detail – POST /opo/onboarding/customers/v1/etb Request: Same as OPO_01
107. OPO_07 OPO detail – POST /opo/onboarding/customers/v1/etb Request: Same as OPO_03
108. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create
109. CIS_11: Get Customer Profile Request: CIS ID Response: cisId, partyCertificateType (idType), identifierType (RMNO, EXTID), identifierTypeValue, partyPrefix, partyFirstName, partyLastname, partyPrefixEn, partyFirstNameEn, partyLastNameEN, partyFullNameEn, partydisplayName, dob, partyBlockedStatus, classificationType, classificationTypevalue, partyChannelStatus, partyChannelBlock
110. CIS ID and Registration Process Instance Key
111. Liveness Check If it passes, proceed the Face comparison
112. AF1: Call appsflyer.initSDK() To send installation event
113. CIS ID, Authlevel = 3
114. Store DigitalID & DeviceBindingKey
115. Generate Key call to CIAM
116. E4: Publish Event Topic: <env>.raw.cis.party.update EventType: account.add, account.update
117. Cache Product details
118. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
119. Fetch Task
120. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
121. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
122. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
123. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
124. API#2: /opo/onboarding/customers/v1/etb/products
125. OPO_05 OPO detail – Start Process, submit task vai gRPC
126. OPO_06: Get Customer Account /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id, bbl-cust-id-token Request: - Response: products
127. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
128. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
129. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
130. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
131. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
132. IAM_16: OPO 01
133. CIAM validates OTP. If it matches, then can proceed further
134. If users already accepted PDPA clause 6, skip to Face verificatoin
135. CIAM checks bblscore. If it equals to 3, then can proceed further
136. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
137. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
138. System token issued by Ping
139. auth ID token – return in every call, change to the new one every call (60 minutes expired)
140. Private API - Group System token issued by Camunda
141. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
142. IAM_11: Update PDPA consent (To-be: IAM_18)
143. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
144. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
145. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
146. IAM_12: Face Comparison Request: requestType =R06/R23 , idNumber= Nationality+idNumber, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
147. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
148. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
149. V2 CIS_Wrapper(7): Create CIS Profile POST: /cis/customer-profile/v2/internal/customers (No token) Request: {party, profile, contactNumber, email, address, agreement, consent, riskProfile, identity, identifier, channel, classification} Action: “CREATE_PROFILE” Response: CISID, partyPrefix, partyFirstName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, classificationType, classificationTypeValue, RMNO, EXTID
150. V1 - CIS_06: Update PDPA consent POST: /cis/v1/customer-onboarding/core/pdpa Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status V2 - CIS_Wrapper (6): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
151. V1 - CIS_09: Add Product to CIS Profile POST: /cis/v1/customers-accounts/customers/accounts Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status V2 - CIS_Wrapper (new) : Add or Update Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
152. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=PDPA}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
153. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
154. If CIS returned errors for update PDPA, then end the flow.
155. If cache not found, then inquiry C2A from RM.
156. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete
157. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table

### Page 3: ETB(MMP Lot2)

1. CIAM (SAAS – no SecureConnect)
2. Apigee (Experience)
3. IAM Proxy (Experience)
4. Apigee (Engagement)
5. 0. Splash screen
6. Cache per session?? TBC design
7. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
8. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
9. 1. Welcome & Orientation
10. 1. First Page
11. Defer to MVP2 Face Liveness check (SDK)
12. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
13. Ask permission for Push Notification & Activity tracking
14. CIAM (SaaS)
15. Start Customer Enrollment Journey Header: X-Language, X-Channel Response: nonce with key/app attestation
16. Generate nonce
17. Submit attestation data Header: X-DPoP-Token, X-DBA-Token Request: key attestation, app attestation Response: device profile collector callback
18. Trust Assurance Service
19. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 2 - Responds back with a DeviceProfileCallback - Response 2.1 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - Response 2.2 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - End flow - Customized error - End flow - OOTB error
20. Remark: Every request to CIAM requires X-DPoP-Token and CIAM needs to validate the DPoP Proof
21. IAM_40: App and Key Attestation Verification Request: platform, nonce, keyMaterial, attestationBundle Response: keyAttestation { trusted, keyStoreType, publicKey }, appAttestation { trusted, riskScore, decision }
22. CIAM validates DPoP proof
23. [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
24. CIAM validates key and app attestation results returned from TAS
25. [AuditLog] IAM Proxy sheet - IAM_40 Response
26. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 2 - Responds back with a DeviceProfileCallback - End flow - Customized error - End flow - OOTB error
27. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
28. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 3 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
29. Back to First Landing
30. 3. Accept T&C
31. [AuditLog] IAM Proxy sheet - IAM_01 Response
32. Auth ID token in the request
33. Auth_ID token (10minutes expired)
34. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
35. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
36. H1: Customer search POST:/esis/customer-services/customers/search Request: ID Type, ID Number Response: ID Type, ID Number, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
37. CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: identityType, identityValue, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob, cisExternalId
38. IAM_02: Customer Search Request: idNum, idType {customerSearch} Response: cisId, cisExternalId, cisIdStatus, channels [], rmNum, dob, isDemoUser, mobileNumber
39. StartProcessByCID Request: citizen ID, DOB, idType, MobileNo Response: citizen ID, DOB, prompt laserCode
40. 4. Input ID & DOB & Mobile No
41. If CIS profile not found or CIS status is invalid, search RM
42. [AuditLog] Inquiry Wrapper – No token
43. Kill switch ‘ENABLE_ETB_FOREIGNERS’ Workaround by hide UI
44. - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
45. MMP Scope include CI, PP (CT 11, 52) only with hide from UI
46. [CIAM validate] - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error
47. [AuditLog] IAM Proxy sheet - IAM_02 Response
48. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response Reactivation - Response 4 - Response NTB - Response 4 - go back to T&C - End flow - Customized error - End flow - OOTB error
49. IAM_26: Customer Risk-Check and Identity Inquiry Request: IdType, idNum Response: idType, riskLevel, riskLevelReasonCode, bblIalCode, idpIalCode, titleNameTh/En, firstNameTh/En, lastNameTh/En, nationality, mobileNumber, channelStatus, profileStatus, ctCode, kycExpiryDate, expirydate, latestMobileNum, contactNum, seqNum, contactType Resource: customerProfileBan, customerIdentity, customerMobileNumber - Thai checks expired date from customerIdentity (SMCS) - Foreigner checks expired date from customerProfileIdentifications.customerRef.identifications[].expiryDate
50. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
51. CIS_Wrapper(4): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan, customerIdentity}, tellerId, photoFlag, dailyFalg, dataTypeFlag Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code
52. [AuditLog] in case Fail Only Inquiry wrapper – No token
53. ID Type is “CI”
54. [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
55. [AuditLog]Inquiry wrapper – No token
56. CIS_Wrapper (5) : Get Customer Mobile Number by RM No POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: RMNO, {customerMobileNumber} Response: latestMobileNumber, contactNum, contactType, ext, seqNum
57. H7: CustomerProfileContactInfoInqService POST: /esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
58. [AuditLog] IAM Proxy sheet - IAM_26 Response
59. [AuditLog] CIS Inquiry Wrapper – no token
60. [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response ETB with MB or NA - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
61. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
62. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
63. [AuditLog] IAM Proxy sheet - IAM_37 Response
64. SubmitChoice NA Request: choices NA Response: citizenId, DOB, prompt LC
65. 5. Verification Options
66. [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
67. Continue to ETB with MB Flow
68. Kill switch ‘ENABLE_ETB_MB’
69. [ActivityLog] Step 5 - ETB Onboarding - Register With NA - Response 5 - Response with Laser Code - End flow - Customized error - End flow - OOTB error
70. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
71. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg, Code, Desc
72. Review Security with SM if need to go through Apigee Engagement (ADR_15)
73. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description Remark: (Restful/XML)
74. 6. Input Laser code
75. [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
76. [AuditLog] IAM Proxy sheet - IAM_05 Response
77. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
78. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: ID Type, ID Number, Name Response: idNum, resultCode, resultDesc
79. [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
80. [AuditLog] IAM Proxy sheet - IAM_06 Response
81. IAM_08: Send SMS OTP Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0 ...
82. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
83. *Send OTP with Mobile No.in CIAM cache from Step 4 (CIAM does not keep Mobile No.)
84. [AuditLog] IAM Proxy sheet - IAM_08 Response
85. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
86. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
87. [AuditLog] IAM Proxy sheet - IAM_37 Response
88. 7. Input OTP
89. [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
90. [AuditLog] IAM Proxy sheet - IAM_09 Response
91. [AuditLog] IAM Proxy sheet - IAM_10 Response
92. [ActivityLog] Step 6 - ETB Onboarding - Verify Mobile using OTP - Response 6.1.1 - Response with PDPA - Response 6.1.2 - Response with Facial Verification - Response - 6.2 - Resend OTP - In flow error Response 6.3.1 - OTP is incorrect (1 attempt) - In flow error Response 6.3.2 - OTP is incorrect (2 attempt) - In flow error Response 6.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
93. 8. Consent PDPA
94. 9. Introduction for face scan
95. [AuditLog] Update Wrapper – No token
96. [CIAM checks] If ETB with IA Profile response state ETB_FC If ETB without IA Profile response state ETB_NP_FC If ETB_MB response state ETB_MB_FC
97. [AuditLog] IAM Proxy sheet - IAM_11v2 Response
98. [ActivityLog] Step 7 - ETB Onboarding - Biometric Data Collection Consent - Response 7.1 - Response with Facial Verification for ETB with NA - Response 7.2 - Response with Facial Verification for ETB with NA and CIAM profile is missing - Response 7.3 - Response with Facial Verification for ETB with MB - End flow - Customized error - End flow - OOTB error
99. Ask Permission for -Camera
100. 10. Face scan
101. [AuditLog] IAM Proxy sheet - IAM_20 Response
102. [AuditLog] IAM Proxy sheet - IAM_37 Response
103. FR – No Liveness SDK, only capture face photo send to compare at backend system
104. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
105. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
106. [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2.1 - 1-4 Face Invalid attempts for ETB with NA - In flow error Response 9.2.2 - 1-4 Face Invalid attempts for ETB with NA and CIAM profile is missing - In flow error Response 9.2.3 - 1-4 Face Invalid attempts for ETB with MB - End flow - Customized error - End flow - OOTB error
107. Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
108. EFM
109. 11. Set up PIN and Reconfirm PIN
110. IAM_38: EFM Request Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
111. [AuditLog] IAM Proxy sheet - IAM_38 Response
112. alt
113. IAM_15 : Reactivation Update T&C Request: cisId, partyAgreementDateTime, partyAgreementVersion, partyAgreementHash, agreementType, agreementTypeValue Action: UPDATE_AGREEMENT Response: Status
114. [Missing_IDM_Profile flag exist in CIAM]
115. CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
116. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 11 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
117. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
118. [ActivityLog] Step 11 - ETB Onboarding - Bind Device - Response 12 - end of the onboarding process - Response 12 - end of the onboarding process (collect Device info) - End flow - Customized error - End flow - OOTB error
119. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
120. [AuditLog] IAM Proxy sheet - IAM_37 Response
121. Onboarding Success
122. CDP
123. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
124. [Missing_IDM_Profile flag does not exist in CIAM]
125. Cache PPI data on redis: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime
126. CIS_Wrapper(4) : Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
127. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
128. Create RegistrationRecord
129. Create Customer Prospect Profile Record
130. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
131. oCRM
132. If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
133. Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
134. [AuditLog] Update wrapper – No token
135. Check duplicate mobile no. and email in existing CIS Profile
136. If found duplicate mobile no.
137. Delete duplicate mobile no.
138. If CIS = Success then start process in Camunda otherwise send failure message.
139. If found duplicate Email
140. Delete duplicate Email
141. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 10 - Response with processInstanceKey - End flow - Customized error - End flow - OOTB error
142. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 11 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
143. CIS ID
144. [AuditLog] IAM Proxy sheet - IAM_16v2 Response
145. If API update Host or Kafka fail, re execute fail process (retry X times)
146. Write fail payload to DB
147. Process daily batch
148. ATM Mgmt.
149. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
150. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
151. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
152. [ActivityLog] Step 11 - ETB Onboarding - Bind Device - Response 12 - end of the onboarding process - Response 12 - end of the onboarding process (collect Device info) - End flow - Customized error - End flow - OOTB error
153. [AuditLog] IAM Proxy sheet - IAM_37 Response
154. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
155. Update Customer Prospect Profile Record
156. Terminate Stale Processes
157. [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
158. [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
159. OPO get EntraID (Virtual ID)
160. Retry 3 times
161. Adobe SDK
162. [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
163. [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
164. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
165. If enroll TSP (above step) fail
166. DEH TSP Services (Engagement)
167. BCIS (CC)
168. CMS
169. 12. Select Product Remark: - Sorting by using card type: 1.) AMEX, 2.) JCB, 3.) VISA, 4.) Master and 5.) UnionPay - Sorting of each card type by using BIN no. (ascending order) - If no image for render in cc, please use “Placeholder-Landscape-Content” Only - If no image for render in ST/IM, please use “Placeholder” Only
170. [AuditLog] Inquiry Wrapper – Token
171. Validate account no. with RM relationship
172. [AuditLog] Update wrapper - Token
173. 13. Onboarding Success
174. [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
175. [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
176. Update RegistrationRecord
177. 14. 3C Introduction
178. Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
179. Always Get Pushed Token from FCM by not consider on PushNotification OS
180. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
181. Control Screen
182. If Fail, then make pendingRegisterFlag is true
183. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
184. CNH
185. APIGee (Experience)
186. IAM proxy (Experience)
187. APIGee (Engagement)
188. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
189. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
190. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
191. CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
192. CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship}, with appId = [ST,CH] and profileOption = “WithCondition” Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type, ownershipCode
193. ETB_OPO_EXP_03: Get Products V2 (New Version) /opo/onboarding/customers/etb/v2/registration/accounts Header: bbl-customer-id Request: - Response: products (accountDisplayName, accountNumber, displayAccountNumber, category, imageUrl, defaultImageURL, order)
194. IAM_11v2: Update PDPA consent Request: idType, idNumber, titleName, firstName, lastName, dob, nationality, consentdate, brCode, channel, purposeCode, purposeFlag - Action: UPDATE_PDPA Response: status
195. Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
196. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
197. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
198. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
199. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
200. V2 - CIS_Wrapper (6): PDPA Consent Inquiry POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: ID, ID Type, {pdpa} Response: Purpose Code, Purpose Flag (all clause)
201. If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
202. Submit device meta data Request: metadata, location, message Response: T&C URL
203. API#1: (New Version + field order) /opo/onboarding/customers/v1/etb/products
204. ETB_OPO_EXP_02 - Submit Products V2 (New Version) OPO API detail - POST /opo/onboarding/customers/etb/v2/registration/accounts/relationship Request: accountNumber Response: Success/Failure
205. Register Device Notification Request: appId = ‘na’, cisId ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
206. ETB_OPO_ENG_02 - Start ETB Registration V2 OPO API detail – POST: ETB_OPO_ENG_02 - Start ETB Registration V2 Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: cis_id,externalId, processInstanceKey
207. CIAM Checks If msgDecision = “A” proceed next step Else return error
208. Publish Event Topic: XXXX Event Type: XXXX
209. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
210. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: email.delete
211. Publish Event Topic: dev.stg.efmconsumer.digitalrisk
212. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
213. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
214. V2 - CIS_Wrapper: Get account in CIS POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: cisId, {account} Response: Account Number, appId, relationshipCode, acctControl1,acctControl2, acctControl3, acctControl4, NCBD Account Type, flexFlag, ...
215. OPO API detail POST /opo/onboarding/customers/v1/etb/registration
216. ETB_OPO_ENG_XX: Submit Products V2 (New Version) OPO detail – POST /opo/onboarding/customers/v1/etb Request: Same as ETB_OPO_EXP_02 - Submit Products V2
217. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
218. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
219. Filter -Not allowed account status -Filter card already linked
220. If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
221. Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
222. [AuditLog] IAM Proxy sheet - IAM_37 Response
223. Submit the TextOutputCallback Request: TextOutputCallback Response: DeviceFingerprintID
224. Submit Device Binding Request: DeviceBindingCallback Response: Access Token, Refresh Token, ID Token
225. Submit Device Binding Request: DeviceBindingCallback Response: Access Token, Refresh Token, ID Token
226. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
227. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
228. CIS ID and Registration Process Instance Key
229. Liveness Check If it passes, proceed the Face comparison
230. E4: Publish Event Topic: <env>.raw.cis.party.update EventType: account.add, account.update
231. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
232. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
233. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
234. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
235. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
236. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
237. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
238. Add product into CIS (TBD) Request: CIS ID, Account Num Response: ???
239. [AuditLog] IAM Proxy sheet - IAM_15 Response
240. GET [MASKED_URL] Header: bbl-cust-id-token, accept-language, bbl-channel, Content-Type Response: Account Type, Account Number, Account Status, Masked card number (with last 4 digit and return CC only), Card reference number (return CC only), Card name (return CC only), Product Code (return CC only), appId
241. Mapping card info, product code and card name and order.
242. TE Config: www-u.bangkokbank.com/-/media/NCBD
243. Map accountDisplayName from prompt
244. API#2: /opo/onboarding/customers/v1/etb/products
245. Fetch Image from TE Config + imageUrl
246. Mapping Field to existing OPO response format. If appId is “CH”, then map - accountDisplayName = cardName - category is “Cards” / “บัตรต่าง ๆ” (depend on language) - accountNumber is accountNum - displayAccountNumber is maskedCardNum - productCode is productCode - order same as response from DEH Else If appId is “ST”or “IM”, then map - accountDisplayName = accountType of DEH (meaning to accountTypeValue of CIS) - category is “Deposit Accounts” / “บัญชีเงินฝาก” (depend on language) - accountNumber is accountNum - displayAccountNumber is “xxx-x-xx” + last 4 digits of accountNum - accountType is accountType - order same as response from DEH
247. 1. Setup imageURL: If appId is “CH”, then send “/Products/CC/{productCode}-Content” Else If appId is “ST” or “IM”, then send “/Products/BB/{accountDisplayName}” 2. Setup defaultImageUrl If appId is “CH”, then send “/Products/CC/Placeholder-Landscape-Content”. Else If appId is “ST” or “IM”, then send “/Products/BB/Placeholder”.
248. OPO API detail – Start Process, submit task vai gRPC POST /opo/onboarding/engine/v2/registration/process/messages/element/submit
249. ETB_OPO_ENG_XX: Get Products V2 (New Version) /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id, bbl-cust-id-token Request: - Response: products (accountDisplayName, accountNumber, displayAccountNumber, appId, category, imageUrl, order, accountType, productCode)
250. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
251. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
252. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
253. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
254. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
255. IAM_01: T&C content Inquiry Header: accept-language Response: version, hash, tandCpage
256. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
257. CIAM validates OTP. If it matches, then can proceed further
258. If users already accepted PDPA clause 6, skip to Face verificatoin
259. CIAM checks bblscore. If it equals to 3, then can proceed further
260. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
261. System token issued by Ping
262. auth ID token – return in every call, change to the new one every call (60 minutes expired)
263. No need to call OPO (Camunda)
264. Create missing IA profile by cisExternalId
265. Private API - Group System token issued by Camunda
266. IAM_09: PDPA consent Inquiry Request: idNum {pdpa} Response: purposeCode, purposeFlag
267. IAM_10: Get PDPA content Header: accept-language Request: onboardingFlowType Response: version, pdpaContent, hash
268. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
269. IAM_20: Face Comparison Request: idNum, requestType = R06/R23, imageFile = string(base64), imageSourceType=I03, requestId = NCIA+transaction ID, requestChannel = NCIA, … idNum - Thai: idNum - Foreigner: nationality|idNum Response: status, requestId, Confidencescore, bblscore
270. IAM_16 v.2: ETB Create Customer Profile CIAM condition - If bblTalCode from IAM26 == "23", sends bblTalUpdatedDatetime that retrieved from IAM26 - else if bblTalCode from IAM26 != "23", sends bblTalUpdatedDatetime that users do the face scan. Request: regType, user, termAndConditions, pdpaConsents - regType is used to separate between ETB and ETB with MB Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
271. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
272. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
273. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
274. H3: CustomerToAcctRel Inquiry (CBRM-RMT2) POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
275. HX: AccountProfileInq POST:esis/account-services/accounts/profile/inquiry Request: AcctCtl1,2,3,4, Account Types (AppID), accountNum, ProfileOption Response: Account Num, relationshipCode, accountStatus, CT Code
276. HX: Get supplementary credit card POST: /esis/card-services/credit-cards/relationship/inquiry Request: index, cardRef Response: index, cardRef, {primaryCardCode, cardType, cardStatus, availableCredit, outstandingBalance, balanceAsOfdate}
277. V2 - CIS_Wrapper (16): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
278. CIS_Wrapper(9): Create CIS Profile POST: /cis/customer-profile/v2/internal/customers (No token) Request: {party, profile, contactNumber, email, address, agreement, consent, riskProfile, identity, identifier, channel, classification, BAN**} Action: “CREATE_PROFILE” Response: CISID, partyPrefix, partyFirstName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, classificationType, classificationTypeValue, RMNO, EXTID
279. CIS_Wrapper (12) : Add Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
280. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=PDPA}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
281. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
282. If CIS returned errors for update T&C, then end the flow.
283. If CIS returned errors for update PDPA, then end the flow.
284. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
285. Mapping response (prepare data for ADD_ACCOUNT) by match product from customer selected with response returned from Get Customer Account Relationship
286. Non sequential step
287. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
288. If profileOption = WithCondition and appId = CH then not return account with puchasing and corporate card (accountNum starts with '[MASKED_CODE]' or '[MASKED_CODE]')
289. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID
290. [AuditLog] IAM Proxy sheet - IAM_36 Response
291. [AuditLog] IAM Proxy sheet - IAM_36 Response

### Page 4: ETB(Post-MMP1)

1. CIAM (SAAS – no SecureConnect)
2. Apigee (Experience)
3. IAM Proxy (Experience)
4. Apigee (Engagement)
5. 0. Splash screen
6. POST MMP1 - Add DWR Device profiling at beginning of onboarding and before request EFM to approval Remark: Since DWN charging model so decided to add at Entry - Support Foreigner (CT: 11, 52)
7. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
8. 1. Welcome & Orientation
9. 1. First Page
10. Defer to MVP2 Face Liveness check (SDK)
11. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
12. Cache per session?? TBC design
13. Ask permission for Push Notification & Activity tracking
14. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
15. CIAM (SaaS)
16. Start Customer Enrollment Journey Header: X-Language, X-Channel Response: nonce with key/app attestation
17. Generate nonce
18. Trust Assurance Service
19. Submit attestation data Header: X-DPoP-Token, X-DBA-Token Request: key attestation, app attestation Response: device profile collector callback
20. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 1 - Responds back with a callback to collect key/app attestation - End flow - Customized error - End flow - OOTB error
21. IAM_40: App and Key Attestation Verification Request: platform, nonce, keyMaterial, attestationBundle Response: keyAttestation { trusted, keyStoreType, publicKey }, appAttestation { trusted, riskScore, decision }
22. CIAM validates DPoP proof
23. Remark: Every request to CIAM requires X-DPoP-Token and CIAM needs to validate the DPoP Proof
24. [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
25. CIAM validates key and app attestation results returned from TAS
26. [AuditLog] IAM Proxy sheet - IAM_40 Response
27. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 2 - Responds back with a DeviceProfileCallback - Response 2.1 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - Response 2.2 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - End flow - Customized error - End flow - OOTB error
28. TBC
29. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
30. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
31. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 3 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
32. Back to First Landing
33. 3. Accept T&C
34. [AuditLog] IAM Proxy sheet - IAM_01 Response
35. Auth ID token in the request
36. Auth_ID token (10minutes expired)
37. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
38. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
39. H1: Customer search POST:/esis/customer-services/customers/search Request: ID Type, ID Number Response: ID Type, ID Number, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
40. CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: identityType, identityValue, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob, cisExternalId
41. IAM_02: Customer Search Request: idNum, idType {customerSearch} Response: cisId, cisExternalId, cisIdStatus, channels [], rmNum, dob, isDemoUser, mobileNumber
42. StartProcessByCID Request: citizen ID, DOB, idType, MobileNo Response: citizen ID, DOB, prompt laserCode
43. 4. Input ID & DOB & Mobile No
44. If CIS profile not found or CIS status is invalid, search RM
45. [AuditLog] Inquiry Wrapper – No token
46. Kill switch ‘ENABLE_ETB_FOREIGNERS’ Workaround by hide UI
47. - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
48. POST MMP 1 Scope include CI, PP (CT 11, 52) only display on screen
49. [CIAM validate] - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error
50. [AuditLog] IAM Proxy sheet - IAM_02 Response
51. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response Reactivation - Response 4 - Response NTB - Response 4 - go back to T&C - End flow - Customized error - End flow - OOTB error
52. IAM_26: Customer Risk-Check and Identity Inquiry Request: IdType, idNum Response: idType, riskLevel, riskLevelReasonCode, bblIalCode, idpIalCode, titleNameTh/En, firstNameTh/En, lastNameTh/En, nationality, mobileNumber, channelStatus, profileStatus, ctCode, kycExpiryDate, expirydate, latestMobileNum, contactNum, seqNum, contactType Resource: customerProfileBan, customerIdentity, customerMobileNumber - Thai checks expired date from customerIdentity (SMCS) - Foreigner checks expired date from customerProfileIdentifications.customerRef.identifications[].expiryDate
53. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
54. CIS_Wrapper(4) Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan, customerIdentity}, tellerId, photoFlag, dailyFalg, dataTypeFlag Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code
55. [AuditLog] in case Fail Only Inquiry wrapper – No token
56. ID Type is “CI”
57. [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
58. [AuditLog]Inquiry wrapper – No token
59. CIS_Wrapper (5) : Get Customer Mobile Number by RM No POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: RMNO, {customerMobileNumber} Response: latestMobileNumber, contactNum, contactType, ext, seqNum
60. H7: CustomerProfileContactInfoInqService POST: /esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
61. [AuditLog] IAM Proxy sheet - IAM_26 Response
62. [AuditLog] CIS Inquiry Wrapper – no token
63. [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response ETB with MB or NA - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
64. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
65. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
66. [AuditLog] IAM Proxy sheet - IAM_37 Response
67. SubmitChoice NA Request: choices NA Response: citizenId, DOB, prompt LC
68. 5. Verification Options
69. [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
70. Continue to ETB with MB Flow
71. Kill switch ‘ENABLE_ETB_MB’
72. [ActivityLog] Step 5 - ETB Onboarding - Register With NA - Response 5 - Response with Laser Code - End flow - Customized error - End flow - OOTB error
73. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
74. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg, Code, Desc
75. Review Security with SM if need to go through Apigee Engagement (ADR_15)
76. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description Remark: (Restful/XML)
77. 6. Input Laser code
78. [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
79. [AuditLog] IAM Proxy sheet - IAM_05 Response
80. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
81. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: ID Type, ID Number, Name Response: idNum, resultCode, resultDesc
82. [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
83. [AuditLog] IAM Proxy sheet - IAM_06 Response
84. IAM_08: Send SMS OTP Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0 ...
85. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
86. *Send OTP with Mobile No.in CIAM cache from Step 4 (CIAM does not keep Mobile No.)
87. [AuditLog] IAM Proxy sheet - IAM_08 Response
88. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
89. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
90. [AuditLog] IAM Proxy sheet - IAM_37 Response
91. 7. Input OTP
92. [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
93. [AuditLog] IAM Proxy sheet - IAM_09 Response
94. [AuditLog] IAM Proxy sheet - IAM_10 Response
95. [ActivityLog] Step 6 - ETB Onboarding - Verify Mobile using OTP - Response 6.1.1 - Response with PDPA - Response 6.1.2 - Response with Facial Verification - Response - 6.2 - Resend OTP - In flow error Response 6.3.1 - OTP is incorrect (1 attempt) - In flow error Response 6.3.2 - OTP is incorrect (2 attempt) - In flow error Response 6.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
96. 8. Consent PDPA
97. 9. Introduction for face scan
98. [AuditLog] Update Wrapper – No token
99. [CIAM checks] If ETB with IA Profile response state ETB_FC If ETB without IA Profile response state ETB_NP_FC If ETB_MB response state ETB_MB_FC
100. [AuditLog] IAM Proxy sheet - IAM_11v2 Response
101. [ActivityLog] Step 7 - ETB Onboarding - Biometric Data Collection Consent - Response 7.1 - Response with Facial Verification for ETB with NA - Response 7.2 - Response with Facial Verification for ETB with NA and CIAM profile is missing - Response 7.3 - Response with Facial Verification for ETB with MB - End flow - Customized error - End flow - OOTB error
102. Ask Permission for -Camera
103. 10. Face scan
104. [AuditLog] IAM Proxy sheet - IAM_20 Response
105. [AuditLog] IAM Proxy sheet - IAM_37 Response
106. FR – No Liveness SDK, only capture face photo send to compare at backend system
107. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
108. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
109. [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2.1 - 1-4 Face Invalid attempts for ETB with NA - In flow error Response 9.2.2 - 1-4 Face Invalid attempts for ETB with NA and CIAM profile is missing - In flow error Response 9.2.3 - 1-4 Face Invalid attempts for ETB with MB - End flow - Customized error - End flow - OOTB error
110. 11. Set up PIN and Reconfirm PIN
111. EFM
112. Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
113. IAM_38: EFM Request Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
114. [AuditLog] IAM Proxy sheet - IAM_38 Response
115. alt
116. [Missing_IDM_Profile flag exist in CIAM]
117. IAM_15 : Reactivation Update T&C Request: cisId, partyAgreementDateTime, partyAgreementVersion, partyAgreementHash, agreementType, agreementTypeValue Action: UPDATE_AGREEMENT Response: Status
118. CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
119. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 11 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
120. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
121. [ActivityLog] Step 11 - ETB Onboarding - Bind Device - Response 12 - end of the onboarding process - Response 12 - end of the onboarding process (collect Device info) - End flow - Customized error - End flow - OOTB error
122. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
123. [AuditLog] IAM Proxy sheet - IAM_37 Response
124. Onboarding Success
125. CDP
126. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
127. [Missing_IDM_Profile flag does not exist in CIAM]
128. Cache PPI data on redis: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime
129. CIS_Wrapper(4): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
130. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
131. Create RegistrationRecord
132. Create Customer Prospect Profile Record
133. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
134. oCRM
135. If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
136. Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
137. [AuditLog] Update wrapper – No token
138. Check duplicate mobile no. and email in existing CIS Profile
139. If found duplicate mobile no.
140. Delete duplicate mobile no.
141. If CIS = Success then start process in Camunda otherwise send failure message.
142. If found duplicate Email
143. Delete duplicate Email
144. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 10 - Response with processInstanceKey - End flow - Customized error - End flow - OOTB error
145. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 11 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
146. CIS ID
147. [AuditLog] IAM Proxy sheet - IAM_16v2 Response
148. If API update Host or Kafka fail, re execute fail process (retry X times)
149. Write fail payload to DB
150. Process daily batch
151. ATM Mgmt.
152. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
153. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
154. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
155. [ActivityLog] Step 11 - ETB Onboarding - Bind Device - Response 12 - end of the onboarding process - Response 12 - end of the onboarding process (collect Device info) - End flow - Customized error - End flow - OOTB error
156. [AuditLog] IAM Proxy sheet - IAM_37 Response
157. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
158. Update Customer Prospect Profile Record
159. Terminate Stale Processes
160. [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
161. [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
162. OPO get EntraID (Virtual ID)
163. Retry 3 times
164. Adobe SDK
165. [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
166. [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
167. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
168. If enroll TSP (above step) fail
169. DEH TSP Services (Engagement)
170. BCIS (CC)
171. CMS
172. 12. Select Product Remark: - Sorting by using card type: 1.) AMEX, 2.) JCB, 3.) VISA, 4.) Master and 5.) UnionPay - Sorting of each card type by using BIN no. (ascending order) - If no image for render in cc, please use “Placeholder-Landscape-Content” Only - If no image for render in ST/IM, please use “Placeholder” Only
173. [AuditLog] Inquiry Wrapper – Token
174. Validate account no. with RM relationship
175. [AuditLog] Update wrapper - Token
176. 13. Onboarding Success
177. [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
178. [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
179. Update RegistrationRecord
180. 14. 3C Introduction
181. Always Get Pushed Token from FCM by not consider on PushNotification OS
182. Control Screen
183. If Fail, then make pendingRegisterFlag is true
184. CNH
185. APIGee (Experience)
186. IAM proxy (Experience)
187. APIGee (Engagement)
188. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
189. IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
190. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
191. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
192. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
193. CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
194. CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship}, with appId = [ST,CH] and profileOption = “WithCondition” Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type, ownershipCode
195. ETB_OPO_EXP_03: Get Products V2 (New Version) /opo/onboarding/customers/etb/v2/registration/accounts Header: bbl-customer-id Request: - Response: products (accountDisplayName, accountNumber, displayAccountNumber, category, imageUrl, defaultImageURL, order)
196. IAM_11v2: Update PDPA consent Request: idType, idNumber, titleName, firstName, lastName, dob, nationality, consentdate, brCode, channel, purposeCode, purposeFlag - Action: UPDATE_PDPA Response: status
197. Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
198. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
199. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
200. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
201. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
202. CIS_Wrapper (6): PDPA Consent Inquiry POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: ID, ID Type, {pdpa} Response: Purpose Code, Purpose Flag (all clause)
203. If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
204. Submit device meta data Request: metadata, location, message Response: T&C URL
205. API#1: (New Version + field order) /opo/onboarding/customers/v1/etb/products
206. ETB_OPO_EXP_02 - Submit Products V2 (New Version) OPO API detail - POST /opo/onboarding/customers/etb/v2/registration/accounts/relationship Request: accountNumber Response: Success/Failure
207. Register Device Notification Request: appId = ‘na’, cisId ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
208. ETB_OPO_ENG_02 - Start ETB Registration V2 OPO API detail – POST: ETB_OPO_ENG_02 - Start ETB Registration V2 Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: cis_id,externalId, processInstanceKey
209. CIAM Checks If msgDecision = “A” proceed next step Else return error
210. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
211. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: email.delete
212. Publish Event Topic: dev.stg.efmconsumer.digitalrisk
213. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
214. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
215. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
216. CIS_Wrapper (11): Get account in CIS POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: cisId, {account} Response: Account Number, appId, relationshipCode, acctControl1,acctControl2, acctControl3, acctControl4, NCBD Account Type, flexFlag, ...
217. OPO API detail POST /opo/onboarding/customers/v1/etb/registration
218. ETB_OPO_ENG_XX: Submit Products V2 (New Version) OPO detail – POST /opo/onboarding/customers/v1/etb Request: Same as ETB_OPO_EXP_02 - Submit Products V2
219. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
220. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
221. Filter -Not allowed account status -Filter card already linked
222. If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
223. Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
224. [AuditLog] IAM Proxy sheet - IAM_37 Response
225. Submit the TextOutputCallback Request: TextOutputCallback Response: DeviceFingerprintID
226. Submit Device Binding Request: DeviceBindingCallback Response: Access Token, Refresh Token, ID Token
227. Submit Device Binding Request: DeviceBindingCallback Response: Access Token, Refresh Token, ID Token
228. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
229. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
230. CIS ID and Registration Process Instance Key
231. Liveness Check If it passes, proceed the Face comparison
232. E4: Publish Event Topic: <env>.raw.cis.party.update EventType: account.add, account.update
233. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
234. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
235. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
236. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
237. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
238. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
239. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
240. Add product into CIS (TBD) Request: CIS ID, Account Num Response: ???
241. [AuditLog] IAM Proxy sheet - IAM_15 Response
242. GET [MASKED_URL] Header: bbl-cust-id-token, accept-language, bbl-channel, Content-Type Response: Account Type, Account Number, Account Status, Masked card number (with last 4 digit and return CC only), Card reference number (return CC only), Card name (return CC only), Product Code (return CC only), appId
243. Mapping card info, product code and card name and order.
244. TE Config: www-u.bangkokbank.com/-/media/NCBD
245. Map accountDisplayName from prompt
246. API#2: /opo/onboarding/customers/v1/etb/products
247. Fetch Image from TE Config + imageUrl
248. Mapping Field to existing OPO response format. If appId is “CH”, then map - accountDisplayName = cardName - category is “Cards” / “บัตรต่าง ๆ” (depend on language) - accountNumber is accountNum - displayAccountNumber is maskedCardNum - productCode is productCode - order same as response from DEH Else If appId is “ST”or “IM”, then map - accountDisplayName = accountType of DEH (meaning to accountTypeValue of CIS) - category is “Deposit Accounts” / “บัญชีเงินฝาก” (depend on language) - accountNumber is accountNum - displayAccountNumber is “xxx-x-xx” + last 4 digits of accountNum - accountType is accountType - order same as response from DEH
249. 1. Setup imageURL: If appId is “CH”, then send “/Products/CC/{productCode}-Content” Else If appId is “ST” or “IM”, then send “/Products/BB/{accountDisplayName}” 2. Setup defaultImageUrl If appId is “CH”, then send “/Products/CC/Placeholder-Landscape-Content”. Else If appId is “ST” or “IM”, then send “/Products/BB/Placeholder”.
250. OPO API detail – Start Process, submit task vai gRPC POST /opo/onboarding/engine/v2/registration/process/messages/element/submit
251. ETB_OPO_ENG_XX: Get Products V2 (New Version) /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id, bbl-cust-id-token Request: - Response: products (accountDisplayName, accountNumber, displayAccountNumber, appId, category, imageUrl, order, accountType, productCode)
252. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
253. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
254. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
255. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
256. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
257. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
258. IAM_01: T&C content Inquiry Header: accept-language Response: version, hash, tandCpage
259. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
260. CIAM validates OTP. If it matches, then can proceed further
261. If users already accepted PDPA clause 6, skip to Face verificatoin
262. CIAM checks bblscore. If it equals to 3, then can proceed further
263. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
264. System token issued by Ping
265. auth ID token – return in every call, change to the new one every call (60 minutes expired)
266. No need to call OPO (Camunda)
267. Create missing IA profile by cisExternalId
268. Private API - Group System token issued by Camunda
269. IAM_09: PDPA consent Inquiry Request: idNum {pdpa} Response: purposeCode, purposeFlag
270. IAM_10: Get PDPA content Header: accept-language Request: onboardingFlowType Response: version, pdpaContent, hash
271. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
272. IAM_20: Face Comparison Request: idNum, requestType = R06/R23, imageFile = string(base64), imageSourceType=I03, requestId = NCIA+transaction ID, requestChannel = NCIA, … idNum - Thai: idNum - Foreigner: nationality|idNum Response: status, requestId, Confidencescore, bblscore
273. IAM_16 v.2: ETB Create Customer Profile CIAM condition - If bblTalCode from IAM26 == "23", sends bblTalUpdatedDatetime that retrieved from IAM26 - else if bblTalCode from IAM26 != "23", sends bblTalUpdatedDatetime that users do the face scan. Request: regType, user, termAndConditions, pdpaConsents - regType is used to separate between ETB and ETB with MB Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
274. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
275. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
276. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
277. H3: CustomerToAcctRel Inquiry (CBRM-RMT2) POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
278. HX: AccountProfileInq POST:esis/account-services/accounts/profile/inquiry Request: AcctCtl1,2,3,4, Account Types (AppID), accountNum, ProfileOption Response: Account Num, relationshipCode, accountStatus, CT Code
279. HX: Get supplementary credit card POST: /esis/card-services/credit-cards/relationship/inquiry Request: index, cardRef Response: index, cardRef, {primaryCardCode, cardType, cardStatus, availableCredit, outstandingBalance, balanceAsOfdate}
280. CIS_Wrapper (16): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
281. CIS_Wrapper(9): Create CIS Profile POST: /cis/customer-profile/v2/internal/customers (No token) Request: {party, profile, contactNumber, email, address, agreement, consent, riskProfile, identity, identifier, channel, classification, BAN**} Action: “CREATE_PROFILE” Response: CISID, partyPrefix, partyFirstName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, classificationType, classificationTypeValue, RMNO, EXTID
282. CIS_Wrapper (12) : Add Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
283. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=PDPA}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
284. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
285. If CIS returned errors for update T&C, then end the flow.
286. If CIS returned errors for update PDPA, then end the flow.
287. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
288. Mapping response (prepare data for ADD_ACCOUNT) by match product from customer selected with response returned from Get Customer Account Relationship
289. Non sequential step
290. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
291. If profileOption = WithCondition and appId = CH then not return account with puchasing and corporate card (accountNum starts with '[MASKED_CODE]' or '[MASKED_CODE]')
292. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID
293. [AuditLog] IAM Proxy sheet - IAM_36 Response
294. [AuditLog] IAM Proxy sheet - IAM_36 Response
295. [AuditLog] IAM Proxy sheet - IAM_36 Response

### Page 5: ETB (FR & MVP0)

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. 1. First Page
4. 2. Welcome Page
5. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
6. Defer to MVP2 Check Wifi/Cellular Check SIM Face Liveness check (SDK)
7. CIAM (SaaS)
8. Ask Permission for -Activity tracking -Push notification
9. 3. Accept T&C
10. T&C-MS/DB
11. Auth_ID token (10minutes expired)
12. Apigee (Engagement)
13. Apigee (Experience)
14. CIAM (SAAS – no SecureConnect)
15. IAM Proxy (Experience)
16. 4. Input ID & DOB
17. TBC -Combine services
18. 5. Input Laser code
19. (Restful/XML)
20. 6. Display Mobile No.
21. User input phone number in FR
22. 7. Input OTP
23. 8. Consent PDPA
24. TBC
25. PDPA content/DB
26. ATM Mgnt
27. 9. Introduction for face scan
28. Ask Permission for -Camera
29. 10. Face scan
30. FR – No Liveness SDK, only capture face photo send to compare at backend system
31. Cache PPI data (Data TBD)
32. If CIS = Success then start process in Camunda otherwise send failure message.
33. 11. Set up PIN and Reconfirm PIN
34. Create RegistrationRecord
35. Create Customer Prospect Profile Record
36. CIS ID
37. Update Customer Prospect Profile Record
38. JWT Token (CIS ID)
39. Terminate Stale Processes
40. If API update CustomerProfileRelAdd fail
41. Check if duplicate mobile no. in CIS Profile
42. If found duplicate mobile no.
43. Delete duplicate mobile no.
44. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
45. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
46. Remove this call.
47. 12. Select Product
48. Read the Cache for the Product details
49. Update RegistrationRecord
50. 13.Suceess
51. Control Screen
52. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
53. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
54. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
55. IAM proxy (Experience)
56. APIGee (Experience)
57. APIGee (Engagement)
58. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
59. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
60. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
61. If Active account – Yes Then, check Risk Level, IAL, CT
62. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
63. OPO_04 OPO API detail - TBC
64. Parallel Task to onboard TSP, PFM, CDP
65. E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
66. E6: Publish Event Event topic: <env>.cis.update.customer.success EventType: ADD_ACCOUNT
67. E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
68. Cache Product details
69. CIS ID and Registration Process Instance Key
70. E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
71. Compare Mobile No. from 2 source If Yes, Send OTP
72. Liveness Check If Yes, do face compare
73. Store DigitalID & DeviceBindingKey in SecureStorage
74. Generate Key call to CIAM
75. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
76. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
77. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
78. E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
79. Fetch Task
80. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
81. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
82. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
83. CDP1: Create CDP Profile -à TBC POST: xxxxxx Request: CISID Response: xxxxx
84. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
85. OPO_06 OPO API detail - TBC
86. OPO_05 OPO detail – Start Process gRPC Call
87. OPO_07 OPO detail – Submit task gRPC Call
88. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
89. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
90. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
91. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
92. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
93. auth ID token – return in every call, change to the new one every call (60 minutes expired)
94. auth ID token in the request
95. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
96. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
97. Get PDPA content (TBD) Request: ??? Response: ???
98. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
99. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
100. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
101. What’s Language?
102. IAM_16 (new) :OPO 01
103. Get T&C content (TBD) Request: ??? Response: SessionID, ???
104. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
105. Submit device meta data Request: metadata, location, message Response: T&C URL
106. System token issued by Ping
107. Review Security with SM if need to go through Apigee Engagement (ADR_15)
108. CIAM checks 1. ctCode = 09 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
109. Private API - Group System token issued by Camunda
110. IAM_01: T&C content Inquiry Request: EN Response: version, tandCUrl
111. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
112. IAM_03: Customer Profile Inquiry Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
113. IAM_04: Get customer ID Card Info
114. IAM_10: Get PDPA content
115. IAM_11: Update PDPA consent
116. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
117. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
118. IAM_12: Face Comparison (photo dipchip Template =I01)
119. IAM_05: Check DOPA
120. IAM_06:Check Customer Suspicious Account
121. IAM_08: Send SMS OTP
122. IAM_07: Get Customer Mobile Numbers
123. IAM_09: PDPA consent Inquiry
124. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
125. CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
126. CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
127. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
128. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
129. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
130. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
131. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
132. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
133. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
134. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
135. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
136. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
137. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
138. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
139. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
140. If Pass, OTP Verification
141. If update PDPA consent fail, ignore and go to next step.
142. If Pass, ID Card Expire
143. If Pass, Mule Account
144. If CIS profile not found or CIS status is invalid, search RM
145. If RM is found, get customer profile from RM
146. If RM is found, get customer account relationship from RM
147. If cache not found, then inquiry C2A from RM.
148. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
149. H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
150. CIAM token in the API request (1st call)

### Page 6: ETB(MMP Lot1)_CDP

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. Host Integration for Registration ETB
4. 1. First Page
5. Apigee (Engagement)
6. Apigee (Experience)
7. CIAM (SAAS – no SecureConnect)
8. IAM Proxy (Experience)
9. 2. Welcome Page
10. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
11. Defer to MVP2 Face Liveness check (SDK)
12. CIAM (SaaS)
13. Ask Permission for -Activity tracking -Push notification
14. 3. Accept T&C
15. Auth_ID token (10minutes expired)
16. 4. Input ID & DOB
17. TBC -Combine services
18. 5. Input Laser code
19. (Restful/XML)
20. 6. Display Mobile No.
21. User input phone number, no check sim
22. 7. Input OTP
23. 8. Consent PDPA
24. 9. Introduction for face scan
25. Ask Permission for -Camera
26. 10. Face scan
27. FR – No Liveness SDK, only capture face photo send to compare at backend system
28. Cache PPI data (Data TBD)
29. If CIS = Success then start process in Camunda otherwise send failure message.
30. 11. Set up PIN and Reconfirm PIN
31. Create RegistrationRecord
32. Create Customer Prospect Profile Record
33. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
34. JWT Token (CIS ID)
35. CIS ID
36. Update Customer Prospect Profile Record
37. Terminate Stale Processes
38. 12. Select Product
39. Read the Cache for the Product details
40. Update RegistrationRecord
41. 13.Suceess
42. Control Screen
43. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
44. IAM proxy (Experience)
45. APIGee (Experience)
46. APIGee (Engagement)
47. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
48. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
49. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
50. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
51. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
52. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
53. OPO_04 OPO API detail - TBC
54. Parallel Task to onboard TSP, PFM
55. Cache Product details
56. CIS ID and Registration Process Instance Key
57. Liveness Check If it passes, proceed the Face comparison
58. AF1: Call appsflyer.initSDK() To send installation event
59. Generate Key call to CIAM
60. Store DigitalID & DeviceBindingKey
61. E2: Event topic: customer.update
62. E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
63. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
64. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
65. Fetch Task
66. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
67. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
68. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
69. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
70. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
71. OPO_06 OPO API detail - TBC
72. OPO_05 OPO detail – Start Process gRPC Call
73. OPO_07 OPO detail – Submit task gRPC Call
74. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
75. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
76. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
77. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
78. Get PDPA content (TBD) Request: ??? Response: ???
79. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
80. auth ID token – return in every call, change to the new one every call (60 minutes expired)
81. auth ID token in the request
82. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
83. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
84. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
85. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
86. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
87. IAM_16: OPO 01
88. Get T&C content (TBD) Request: ??? Response: SessionID, ???
89. CIAM validates OTP. If it matches, then can proceed further
90. If users already accepted PDPA clause 6, skip to Face verificatoin
91. CIAM checks bblscore. If it equals to 3, then can proceed further
92. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
93. Submit device meta data Request: metadata, location, message Response: T&C URL
94. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
95. System token issued by Ping
96. Review Security with SM if need to go through Apigee Engagement (ADR_15)
97. CIAM checks 1. ctCode = 09 (To-be: check ctCode & idType in MMP) 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
98. CIAM checks ID card expired date, allow to continue if expired date is today
99. Private API - Group System token issued by Camunda
100. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
101. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
102. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
103. IAM_03: Customer Profile Inquiry (To-be: IAM_13) Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
104. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
105. IAM_11: Update PDPA consent (To-be: IAM_18)
106. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
107. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
108. IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
109. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
110. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
111. IAM_08: Send SMS OTP Request: mobileNum Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
112. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
113. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
114. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
115. CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
116. CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
117. CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
118. CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
119. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
120. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
121. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
122. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
123. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
124. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
125. CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
126. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
127. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
128. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
129. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
130. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
131. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
132. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
133. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
134. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
135. If CIS returned errors for update PDPA, then end the flow.
136. If CIS profile not found or CIS status is invalid, search RM
137. If RM is found, get customer profile from RM
138. If RM is found, get customer account relationship from RM
139. If cache not found, then inquiry C2A from RM.
140. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
141. CIAM token in the API request (1st call)

### Page 7: ETB(MMP Lot2)_CDP

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. Host Integration for Registration ETB
4. 1. First Page
5. Apigee (Engagement)
6. Apigee (Experience)
7. CIAM (SAAS – no SecureConnect)
8. IAM Proxy (Experience)
9. 2. Welcome Page
10. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
11. Defer to MVP2 Face Liveness check (SDK)
12. CIAM (SaaS)
13. Ask Permission for -Activity tracking -Push notification
14. 3. Accept T&C
15. Auth_ID token (10minutes expired)
16. 4. Input ID & DOB
17. TBC -Combine services
18. 5. Input Laser code
19. (Restful/XML)
20. 6. Display Mobile No.
21. User input phone number, no check sim
22. 7. Input OTP
23. 8. Consent PDPA
24. 9. Introduction for face scan
25. Ask Permission for -Camera
26. 10. Face scan
27. FR – No Liveness SDK, only capture face photo send to compare at backend system
28. Cache PPI data (Data TBD)
29. If CIS = Success then start process in Camunda otherwise send failure message.
30. 11. Set up PIN and Reconfirm PIN
31. Create RegistrationRecord
32. Create Customer Prospect Profile Record
33. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
34. JWT Token (CIS ID)
35. CIS ID
36. Update Customer Prospect Profile Record
37. Terminate Stale Processes
38. 12. Select Product
39. Read the Cache for the Product details
40. Update RegistrationRecord
41. 13.Suceess
42. Control Screen
43. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
44. IAM proxy (Experience)
45. APIGee (Experience)
46. APIGee (Engagement)
47. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
48. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
49. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
50. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
51. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
52. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
53. OPO_04 OPO API detail - TBC
54. Parallel Task to onboard TSP, PFM
55. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
56. CDP2: Update Identity
57. CDP3: Update onboard success
58. Cache Product details
59. CIS ID and Registration Process Instance Key
60. Liveness Check If it passes, proceed the Face comparison
61. AF1: Call appsflyer.initSDK() To send installation event
62. Generate Key call to CIAM
63. Store DigitalID & DeviceBindingKey
64. E2: Event topic: customer.update
65. E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
66. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
67. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
68. Fetch Task
69. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
70. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
71. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
72. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
73. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
74. OPO_06 OPO API detail - TBC
75. OPO_05 OPO detail – Start Process gRPC Call
76. OPO_07 OPO detail – Submit task gRPC Call
77. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
78. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
79. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
80. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
81. Get PDPA content (TBD) Request: ??? Response: ???
82. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
83. auth ID token – return in every call, change to the new one every call (60 minutes expired)
84. auth ID token in the request
85. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
86. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
87. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
88. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
89. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
90. IAM_16: OPO 01
91. Get T&C content (TBD) Request: ??? Response: SessionID, ???
92. CIAM validates OTP. If it matches, then can proceed further
93. If users already accepted PDPA clause 6, skip to Face verificatoin
94. CIAM checks bblscore. If it equals to 3, then can proceed further
95. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
96. Submit device meta data Request: metadata, location, message Response: T&C URL
97. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
98. System token issued by Ping
99. Review Security with SM if need to go through Apigee Engagement (ADR_15)
100. CIAM checks 1. ctCode = 09 (To-be: check ctCode & idType in MMP) 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
101. CIAM checks ID card expired date, allow to continue if expired date is today
102. Private API - Group System token issued by Camunda
103. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
104. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
105. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
106. IAM_03: Customer Profile Inquiry (To-be: IAM_13) Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
107. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
108. IAM_11: Update PDPA consent (To-be: IAM_18)
109. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
110. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
111. IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
112. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
113. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
114. IAM_08: Send SMS OTP Request: mobileNum Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
115. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
116. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
117. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
118. CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
119. CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
120. CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
121. CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
122. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
123. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
124. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
125. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
126. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
127. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
128. CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
129. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
130. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
131. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
132. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
133. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
134. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
135. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
136. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
137. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
138. If CIS returned errors for update PDPA, then end the flow.
139. If CIS profile not found or CIS status is invalid, search RM
140. If RM is found, get customer profile from RM
141. If RM is found, get customer account relationship from RM
142. If cache not found, then inquiry C2A from RM.
143. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
144. CIAM token in the API request (1st call)

### Page 8: ETB_Host (MMP Lot2)

1. 0A.Splash
2. 1. First Page
3. 2. Welcome Page
4. Ask Permission for -Activity tracking -Push notification
5. After clicking Sign up, then check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
6. 3. Accept T&C
7. AcceptT&C
8. 4. Input ID & DOB & Mobile No
9. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
10. - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
11. MMP Scope include CI, PP (CT 11, 52) only
12. H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
13. [Checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
14. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
15. [Checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
16. [Checks #3] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_04 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
17. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
18. 5. Verification Options
19. Continue to ETB with MB Flow
20. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description Remark: (Restful/XML)
21. 6. Input Laser code
22. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
23. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
24. 7. Input OTP
25. 8. Consent PDPA
26. 9. Introduction for face scan
27. Ask Permission for -Camera
28. 10. Face scan
29. (NEW) H22: Request For Approve Transaction
30. EFM
31. 11. Set up PIN and Reconfirm PIN
32. H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
33. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
34. oCRM
35. If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
36. Create profile at NCBD (CIS ID)
37. ATM Mgmt.
38. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
39. 12. Select Product
40. Add Product into CIS
41. 13.Suceess
42. Control Screen
43. [Validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
44. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
45. Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
46. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
47. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
48. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
49. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
50. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
51. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
52. Start Flow
53. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
54. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
55. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription

### Page 9: ETB_Host (FR)

1. 4. Input ID & DOB
2. TBC -Combine services
3. 5. Input Laser code
4. (Restful/XML)
5. 6. Display Mobile No.
6. User input phone number (for Foundation release)
7. Check If Mobile number is in RM profile, Send OTP if pass
8. 7. Input OTP
9. Display PDPA screen if user haven’t given consent.
10. 8. Consent PDPA
11. 9. Introduction for face scan
12. 10. Face scan
13. Create profile at NCBD (CIS ID)
14. 11. Set up PIN and Reconfirm PIN
15. 12. Select Product
16. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
17. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
18. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
19. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
20. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
21. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record
22. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
23. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
24. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
25. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
26. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID Card Photo, First name, Last name
27. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
28. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
29. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
30. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
31. Check Card Expire, ID card photo.
32. If CIS profile not found or CIS status is invalid, search RM
33. If RM is found, and DOB is correct, get customer profile from RM
34. If RM is found, get customer account relationship from RM
35. If cache not found, then inquiry C2A from RM
36. Check Risk Rating and IAL If Pass, get ID card information

### Page 10: ETB (MVP0) Backup

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. Host Integration for Registration ETB
4. 1. First Page
5. 2. Welcome Page
6. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
7. Defer to MVP2 Face Liveness check (SDK)
8. CIAM (SaaS)
9. Ask Permission for -Activity tracking -Push notification
10. 3. Accept T&C
11. T&C-MS/DB
12. Auth_ID token (10minutes expired)
13. Apigee (Engagement)
14. Apigee (Experience)
15. CIAM (SAAS – no SecureConnect)
16. IAM Proxy (Experience)
17. 4. Input ID & DOB
18. TBC -Combine services
19. 5. Input Laser code
20. (Restful/XML)
21. 6. Display Mobile No.
22. User input phone number, no check sim
23. 7. Input OTP
24. 8. Consent PDPA
25. TBC
26. PDPA content/DB
27. 9. Introduction for face scan
28. Ask Permission for -Camera
29. 10. Face scan
30. FR – No Liveness SDK, only capture face photo send to compare at backend system
31. Cache PPI data (Data TBD)
32. If CIS = Success then start process in Camunda otherwise send failure message.
33. 11. Set up PIN and Reconfirm PIN
34. Create RegistrationRecord
35. Create Customer Prospect Profile Record
36. CIS ID
37. Update Customer Prospect Profile Record
38. JWT Token (CIS ID)
39. Terminate Stale Processes
40. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
41. Remove this call.
42. 12. Select Product
43. Read the Cache for the Product details
44. Update RegistrationRecord
45. 13.Suceess
46. Control Screen
47. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
48. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
49. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
50. IAM proxy (Experience)
51. APIGee (Experience)
52. APIGee (Engagement)
53. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
54. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
55. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
56. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
57. OPO_04 OPO API detail - TBC
58. Parallel Task to onboard TSP, PFM, CDP
59. Cache Product details
60. CIS ID and Registration Process Instance Key
61. Liveness Check If it passes, proceed the Face comparison
62. Generate Key call to CIAM
63. Store DigitalID & DeviceBindingKey
64. E2: Event topic: customer.update
65. E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
66. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
67. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
68. Fetch Task
69. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
70. CDP1: Create CDP Profile -à TBC POST: xxxxxx Request: CISID Response: xxxxx
71. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
72. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
73. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
74. OPO_06 OPO API detail - TBC
75. OPO_05 OPO detail – Start Process gRPC Call
76. OPO_07 OPO detail – Submit task gRPC Call
77. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
78. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
79. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
80. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
81. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
82. auth ID token – return in every call, change to the new one every call (60 minutes expired)
83. auth ID token in the request
84. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
85. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
86. Get PDPA content (TBD) Request: ??? Response: ???
87. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
88. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
89. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
90. IAM_16: OPO 01
91. Get T&C content (TBD) Request: ??? Response: SessionID, ???
92. CIAM validates OTP. If it matches, then can proceed further
93. If users already accepted PDPA clause 6, skip to Face verificatoin
94. CIAM checks bblscore. If it equals to 3, then can proceed further
95. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
96. Submit device meta data Request: metadata, location, message Response: T&C URL
97. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
98. System token issued by Ping
99. Review Security with SM if need to go through Apigee Engagement (ADR_15)
100. CIAM checks 1. ctCode = 09 (To-be: check ctCode & idType in MMP) 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
101. CIAM checks ID card expired date, allow to continue if expired date is today
102. Private API - Group System token issued by Camunda
103. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
104. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
105. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
106. IAM_03: Customer Profile Inquiry (To-be: IAM_13) Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
107. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
108. IAM_11: Update PDPA consent (To-be: IAM_18)
109. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
110. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
111. IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
112. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
113. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
114. IAM_08: Send SMS OTP Request: mobileNum Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
115. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
116. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
117. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
118. CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
119. CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
120. CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
121. CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
122. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
123. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
124. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
125. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
126. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
127. CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
128. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
129. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
130. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
131. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
132. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
133. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
134. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
135. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
136. If CIS returned errors for update PDPA, then end the flow.
137. If CIS profile not found or CIS status is invalid, search RM
138. If RM is found, get customer profile from RM
139. If RM is found, get customer account relationship from RM
140. If cache not found, then inquiry C2A from RM.
141. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
142. CIAM token in the API request (1st call)

### Page 11: ETB (MMP)_Backup

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. 1. First Page
4. 2. Welcome Page
5. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
6. Defer to MVP2 Face Liveness check (SDK)
7. CIAM (SaaS)
8. Ask Permission for -Activity tracking -Push notification
9. 3. Accept T&C
10. Auth_ID token (10minutes expired)
11. 4. Input ID & DOB
12. 5. Input Laser code
13. (Restful/XML)
14. 6. Display Mobile No.
15. User input phone number, no check sim
16. 7. Input OTP
17. 8. Consent PDPA
18. ATM Mgnt
19. 9. Introduction for face scan
20. Ask Permission for -Camera
21. 10. Face scan
22. FR – No Liveness SDK, only capture face photo send to compare at backend system
23. Cache PPI data (Data TBD)
24. 11. Set up PIN and Reconfirm PIN
25. If CIS = Success then start process in Camunda otherwise send failure message.
26. Create RegistrationRecord
27. Create Customer Prospect Profile Record
28. Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
29. Check duplicate mobile no. and email in existing CIS Profile
30. If found duplicate mobile no.
31. Delete duplicate mobile no.
32. [QA] CIS will update to KAFKA then IAM subscribe for recheck flag hasMobile No.
33. Process daily batch
34. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
35. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
36. TBC: Power make common service for record audit log into Kafka
37. JWT Token
38. CIS ID
39. Update Customer Prospect Profile Record
40. Terminate Stale Processes
41. Remove this call.
42. Update RegistrationRecord
43. 12. Select Product
44. Read the Cache for the Product details
45. 13.Suceess
46. Control Screen
47. Apigee (Engagement)
48. Apigee (Experience)
49. CIAM (SAAS – no SecureConnect)
50. IAM Proxy (Experience)
51. Get
52. V1 - CIS_06: Update PDPA consent POST: /cis/v1/customer-onboarding/core/pdpa Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status V2 - CIS_Wrapper (6): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
53. V1 - CIS_04: Get Customer Mobile Numbers POST: /cis/v1/customer-onboarding/inquiry/mobile Request: RM No. Response: mobileNumberList (90-97, 99) V2 - CIS_Wrapper (4): Customer Mobile Numbers POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: RM No., {customerMobileNumber} Response: contactNum, contactType, seqNum
54. V1 - CIS_05: PDPA Consent Inquiry (Clause 6) POST: /cis/v1/customer-onboarding/core/pdpa Request: ID, ID Type Response: Purpose Code, Purpose Flag (for clause 6 only) V2 - CIS_Wrapper (5): PDPA Consent Inquiry POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: ID, ID Type, {pdpa} Response: Purpose Code, Purpose Flag (all clause)
55. V1 - CIS_03: Get Customer ID Card Info POST: /cis/v1/customer-onboarding/inquiry/identity Request: CitizenID Response: ID expiry date, First name, Last name, Title V2 - CIS_Wrapper (3): Get Customer ID Card Info POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: CitizenID,photFlag, tellerId, dailyFlag, dataTypeFlag, {customerIdentity} Response: ID expiry date, First name, Last name, Title
56. H9: PDPAConsentInq POST: /PDPA/consent/inquiry Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
57. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
58. H10: PDPAConsentUpdate POST: /PDPA/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
59. IAM proxy (Experience)
60. APIGee (Experience)
61. APIGee (Engagement)
62. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
63. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
64. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
65. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
66. OPO_04 OPO API detail - TBC
67. Parallel Task to onboard TSP, PFM, CDP
68. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create
69. Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
70. Cache Product details
71. Validate account no. with RM relationship
72. CIS ID and Registration Process Instance Key
73. E4: Publish Event Topic: <env>.raw.cis.party.update EventType: account.add, account.update
74. Liveness Check If it passes, proceed the Face comparison
75. CIS ID, Authlevel = 3
76. Store DigitalID & DeviceBindingKey
77. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
78. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
79. Fetch Task
80. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
81. CDP1: Create CDP Profile -à TBC POST: xxxxxx Request: CISID Response: xxxxx
82. H12: CustomerService-CustomerProfileRelAdd POST: /cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
83. H13: CustomerProfileIALMoD PUT: /esis/customer-services/customers/profiles/ial Request: RM no., IAL Info Response: status, result
84. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
85. OPO_06 OPO API detail - TBC
86. OPO_05 OPO detail – Start Process gRPC Call
87. OPO_07 OPO detail – Submit task gRPC Call
88. H1: searchCust POST: /esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
89. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
90. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
91. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
92. Get PDPA content (TBD) Request: ??? Response: ???
93. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
94. auth ID token – return in every call, change to the new one every call (60 minutes expired)
95. auth ID token in the request
96. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
97. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
98. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
99. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
100. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
101. IAM_16: OPO 01
102. Get T&C content (TBD) Request: ??? Response: SessionID, ???
103. CIAM validates OTP. If it matches, then can proceed further
104. If users already accepted PDPA clause 6, skip to Face verificatoin
105. CIAM checks bblscore. If it equals to 3, then can proceed further
106. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
107. Submit device meta data Request: metadata, location, message Response: T&C URL
108. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
109. System token issued by Ping
110. Review Security with SM if need to go through Apigee Engagement (ADR_15)
111. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
112. CIAM checks 1. ctCode = 09 (To-be: check ctCode & idType in MMP) 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
113. CIAM checks ID card expired date, allow to continue if expired date is today
114. Private API - Group System token issued by Camunda
115. V1 - CIS_02: Customer Profile Inquiry (for SAAS) POST: /cis/v1/customer-onboarding/inquiry/profile/accounts Request: RM No. Response: CT, KYC risk level, KYC risk reason code, BBLIAL, Flag Has Active Accounts V2 - CIS_Wrapper (2): Get customer Profile POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: rmNum, {customerProfile, customerProfileKyc, customerProfileIalInfo} Response: RM No., ctCode, gender, customerStatus, nationality, firstName, lastName, type, riskLevel, riskReason, bblIalCode, idpIalCode
116. V1 - CIS_01: Customer Search by Citizen ID POST: /cis/v1/customer-onboarding/inquiry/profile Request: idNum Response: DoB, RM No. or CIS No., CIS status V2 - CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
117. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
118. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
119. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
120. IAM_03: Customer Profile Inquiry (To-be: IAM_13) Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
121. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
122. IAM_11: Update PDPA consent (To-be: IAM_18)
123. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
124. IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
125. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
126. IAM_08: Send SMS OTP Request: mobileNum Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
127. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
128. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
129. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
130. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
131. CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
132. CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
133. V2 CIS_Wrapper(7): Create CIS Profile POST: /cis/customer-profile/v2/internal/customers (No token) Request: {party, profile, contactNumber, email, address, agreement, consent, riskProfile, identity, identifier, channel, classification} Action: “CREATE_PROFILE” Response: CISID, partyPrefix, partyFirstName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, classificationType, classificationTypeValue, RMNO, EXTID
134. V1 - CIS_08: Get Customer Account Relationship POST: /cis/v1/customers-accounts/inquiry/account Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship) V2 - CIS_Wrapper (8): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
135. V1 - CIS_09: Add Product to CIS Profile POST: /cis/v1/customers-accounts/customers/accounts Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status V2 - CIS_Wrapper (new) : Add or Update Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_OR_UPDATE_ACCOUNT” Response: status
136. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
137. CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
138. H2: Customer Profile Inquiry POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: Risk Rating, IAL, firstname, lastname
139. H4: RequestIdentityInfo POST: /smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
140. H7: CustomerProfileContactInfoInqService POST: /esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
141. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
142. H3: CustomerToAcctRel Inquiry POST: /esis/channel-services/customers/accounts/relationship/inquiry Request: RM, AppID Response: accountNumber, acctControl1-4, relationshipCode, accountStatus, accountProdCode
143. H3: CustomerToAcctRel Inquiry POST: /esis/channel-services/customers/accounts/relationship/inquiry Request: RM, AppID Response: accountNumber, acctControl1-4, relationshipCode, accountStatus, accountProdCode
144. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
145. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
146. If CIS returned errors for update PDPA, then end the flow.
147. If CIS profile not found or CIS status is invalid, search RM
148. If RM is found, get customer profile from RM
149. If cache not found, then inquiry C2A from RM.
150. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete
151. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
152. CIAM token in the API request (1st call)

### Page 12: ETB(MMP Lot2)_Backup

1. Cache per session?? TBC design
2. CIAM (SAAS – no SecureConnect)
3. Apigee (Experience)
4. IAM Proxy (Experience)
5. Apigee (Engagement)
6. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
7. 0. Splash screen
8. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
9. 1. Welcome & Orientation
10. 1. First Page
11. CIAM (SaaS)
12. Ask permission for Push Notification & Activity tracking
13. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
14. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 1 - Responds back with a DeviceProfileCallback - Response 2 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
15. Back to First Landing
16. 3. Accept T&C
17. [AuditLog] IAM Proxy sheet - IAM_01 Response
18. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
19. Auth ID token in the request
20. Auth_ID token (10minutes expired)
21. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
22. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
23. V2 - CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
24. StartProcessByCID Request: citizen ID, DOB, idType, MobileNo Response: citizen ID, DOB, prompt laserCode
25. IAM_02: Customer Search Request: idNum, idType {customerSearch} Response: cisId, cisExternalId, cisIdStatus, channels [], rmNum, dob, isDemoUser, mobileNumber
26. 4. Input ID & DOB & Mobile No
27. If CIS profile not found or CIS status is invalid, search RM
28. Kill switch ‘ENABLE_ETB_FOREIGNERS’
29. [AuditLog] Inquiry Wrapper – No token
30. - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
31. MMP Scope include CI, PP (CT 11, 52) only
32. [AuditLog] IAM Proxy sheet - IAM_02 Response
33. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response Reactivation - Response 4 - Response NTB - Response 4 - go back to T&C - End flow - Customized error - End flow - OOTB error
34. IAM_26: Customer Risk-Check and Identity Inquiry Request: IdType, idNum {customerProfileBan, customerIdentity} Response: idType, riskLevel, riskLevelReasonCode, bblIalCode, idpIalCode, titleNameTh/En, firstNameTh/En, lastNameTh/En, nationality, mobileNumber, channelStatus, profileStatus, ctCode, kycExpiryDate, expirydate - Thai checks expired date from customerIdentity (SMCS) - Foreigner checks expired date from customerProfileIdentifications.customerRef.identifications[].expiryDate
35. V2 - CIS_Wrapper (2): Get customer Profile POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: IdType, idNum, {customerProfileBan, customerIdentity} Response: RM No., ctCode, gender, customerStatus, nationality, firstName, lastName, type, riskLevel, riskReason, bblIalCode, idpIalCode
36. If RM is found, get customer profile from RM
37. [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
38. H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
39. [CIAM checks] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_05 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
40. [AuditLog] in case Fail Only Inquiry wrapper – No token
41. [AuditLog] IAM Proxy sheet - IAM_26 Response
42. [AuditLog] in case Fail Only Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - End flow - Customized error - End flow - OOTB error
43. [CIAM checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
44. IAM_07v2: Customer Mobile Inquiry (RM) Request: rmNumber {customerMobileNumber} Response: latestMobileNumber, mobileNumbers
45. V2 - CIS_Wrapper (4): Customer Mobile Numbers POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: RM No., {customerMobileNumber} Response: contactNum, contactType, seqNum
46. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
47. [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response (ETB with MB or NA) - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
48. [AuditLog] IAM Proxy sheet - IAM_07_V2 Response
49. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
50. SubmitChoice NA Request: choices NA Response: citizenId, DOB, prompt LC
51. 5. Verification Options
52. [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
53. Continue to ETB with MB Flow
54. Kill switch ‘ENABLE_ETB_MB’
55. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg, Code, Desc
56. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
57. Review Security with SM if need to go through Apigee Engagement (ADR_15)
58. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description Remark: (Restful/XML)
59. 6. Input Laser code
60. [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
61. [AuditLog] IAM Proxy sheet - IAM_05 Response
62. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
63. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
64. [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
65. [AuditLog] IAM Proxy sheet - IAM_06 Response
66. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
67. [ActivityLog] IAM Proxy sheet - IAM_06 Response
68. IAM_08: Send SMS OTP Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0 ...
69. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
70. *Send OTP with Mobile No.in CIAM cache from Step 4 (CIAM does not keep Mobile No.)
71. [AuditLog] IAM Proxy sheet - IAM_08 Response
72. 7. Input OTP
73. [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
74. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
75. [AuditLog] IAM Proxy sheet - IAM_09 Response
76. 8. Consent PDPA
77. [AuditLog] IAM Proxy sheet - IAM_10 Response
78. [ActivityLog] Step 6 - ETB Onboarding - Verify Mobile using OTP - Response 6.1.1 - Response with PDPA - Response 6.1.2 - Response with Facial Verification - Response - 6.2 - Resend OTP - In flow error Response 6.3.1 - OTP is incorrect (1 attempt) - In flow error Response 6.3.2 - OTP is incorrect (2 attempt) - In flow error Response 6.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
79. 9. Introduction for face scan
80. [AuditLog] Update Wrapper – No token
81. [ActivityLog] Step 7 - ETB Onboarding - Biometric Data Collection Consent - Response 7 - Response with Facial Verification - End flow - Customized error - End flow - OOTB error
82. [AuditLog] IAM Proxy sheet - IAM_11 Response
83. Ask Permission for -Camera
84. 10. Face scan
85. [AuditLog] IAM Proxy sheet - IAM_20 Response
86. [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error
87. FR – No Liveness SDK, only capture face photo send to compare at backend system
88. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
89. POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
90. EFM
91. 11. Set up PIN and Reconfirm PIN
92. Cache PPI data on redis: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime
93. CIS_Wrapper() (new): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
94. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
95. Create RegistrationRecord
96. Create Customer Prospect Profile Record
97. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 10 - Response with processInstanceKey - Response 11 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
98. CH24
99. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
100. oCRM
101. If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
102. Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
103. [AuditLog] Update wrapper – No token
104. Check duplicate mobile no. and email in existing CIS Profile
105. If found duplicate mobile no.
106. Delete duplicate mobile no.
107. [AuditLog] IAM Proxy sheet - IAM_31 Response
108. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 10 - Response with processInstanceKey - End flow - Customized error - End flow - OOTB error
109. If CIS = Success then start process in Camunda otherwise send failure message.
110. [ActivityLog] Step 10 - ETB Onboarding - Register PIN - Response 11 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
111. CIS ID
112. [AuditLog] - actType = 'KAFKA_EVENT_CONSUME' - actSubType = <env>.raw.cis.party.update
113. [ActivityLog] Step 11 - ETB Onboarding - Bind Device - Response 12 - end of the onboarding process - End flow - Customized error - End flow - OOTB error
114. [AuditLog] - actSubType = 'RM Add Relationship'
115. JWT Token
116. [AuditLog] - actSubType = 'RM Update IAL'
117. Process daily batch
118. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
119. ATM Mgmt.
120. H16: File - Batch Pre DAF File (Account no., Account control1,2,3,4)
121. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
122. Update Customer Prospect Profile Record
123. Terminate Stale Processes
124. [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
125. [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
126. OPO get EntraID (Virtual ID)
127. Retry 3 times
128. AppsFlyer
129. [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
130. [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
131. Darwinium
132. [AuditLog] Login - Device Login - Log Location (Lat/Long) in scope MMP Lot#2
133. [AuditLog]Inquiry Wrapper – Token
134. 12. Select Product
135. Read the Cache for the Product details
136. Validate account no. with RM relationship
137. [AuditLog] Update wrapper - Token
138. 13. Onboarding Success
139. [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
140. [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
141. Update RegistrationRecord
142. Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
143. Get Pushed Token from FCM
144. 14. 3C Introduction
145. Control Screen
146. CNH
147. APIGee (Experience)
148. IAM proxy (Experience)
149. APIGee (Engagement)
150. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error If pass above dob validation then check - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’ and has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
151. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
152. V2 - CIS_Wrapper (8): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
153. OPO_02: Get Customer Account /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id Request: - Response: products
154. CIAM checks if there is no Missing_IDM_Profile flag in nodeState, call IAM_31 Else call IAM_15
155. IAM_11v2: Update PDPA consent Request: idType, idNumber, titleName, firstName, lastName, dob, nationality, consentdate, brCode, channel, purposeCode, purposeFlag - Action: UPDATE_PDPA Response: status
156. Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
157. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
158. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
159. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
160. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
161. V2 - CIS_Wrapper (5): PDPA Consent Inquiry POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: ID, ID Type, {pdpa} Response: Purpose Code, Purpose Flag (all clause)
162. Submit device meta data Request: metadata, location, message Response: T&C URL
163. API#1: /opo/onboarding/customers/v1/etb/products
164. OPO_03: Add Account to CIS OPO API detail - POST /opo/onboarding/customers/v1/etb/registration Request: products Response: Success/Failure
165. Register Device Notification Request: appId = ‘na’, cisId ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
166. ETB_OPO_ENG_02 - Start ETB Registration V2 OPO API detail – POST: ETB_OPO_ENG_02 - Start ETB Registration V2 Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: cis_id,externalId, processInstanceKey
167. Publish Event Topic: XXXX Event Type: XXXX
168. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
169. Send DWR Profile and Access token in background
170. OPO_04 OPO API detail – POST /opo/onboarding/customers/v1/etb Request: Same as OPO_01
171. OPO_07 OPO detail – POST /opo/onboarding/customers/v1/etb Request: Same as OPO_03
172. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
173. Submit the TextOutputCallback Request: TextOutputCallback Response: DeviceFingerprintID
174. Submit Device Binding Request: DeviceBindingCallback Response: Access Token, Refresh Token, ID Token
175. CIS ID and Registration Process Instance Key
176. Liveness Check If it passes, proceed the Face comparison
177. AF1: Call appsflyer.initSDK() To send installation event
178. Store DigitalID & DeviceBindingKey
179. CIS ID, Authlevel = 3
180. E4: Publish Event Topic: <env>.raw.cis.party.update EventType: account.add, account.update
181. Cache Product details
182. Fetch Task
183. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
184. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
185. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
186. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
187. API#2: /opo/onboarding/customers/v1/etb/products
188. OPO_05 OPO detail – Start Process, submit task vai gRPC
189. OPO_06: Get Customer Account /opo/onboarding/customers/v1/etb/products Header: bbl-customer-id, bbl-cust-id-token Request: - Response: products
190. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
191. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
192. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
193. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
194. IAM_01: T&C content Inquiry Header: accept-language Response: version, hash, tandCpage
195. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
196. CIAM validates OTP. If it matches, then can proceed further
197. If users already accepted PDPA clause 6, skip to Face verificatoin
198. CIAM checks bblscore. If it equals to 3, then can proceed further
199. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
200. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
201. System token issued by Ping
202. auth ID token – return in every call, change to the new one every call (60 minutes expired)
203. Private API - Group System token issued by Camunda
204. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
205. IAM_09: PDPA consent Inquiry Request: idNum {pdpa} Response: purposeCode, purposeFlag
206. IAM_10: Get PDPA content Header: accept-language Request: onboardingFlowType Response: version, pdpaContent, hash
207. IAM_31: ETB Create Customer Profile Request: customerProfile, contactInfo, termAndConditions, pdpaConsents, ... Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
208. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
209. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
210. IAM_20: Face Comparison Request: idNum, requestType = R06/R23, imageFile = string(base64), imageSourceType=I03, requestId = NCIA+transaction ID, requestChannel = NCIA, … idNum - Thai: idNum - Foreigner: nationality|idNum Response: status, requestId, Confidencescore, bblscore
211. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
212. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
213. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
214. V2 - CIS_Wrapper (6): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
215. V2 CIS_Wrapper(7): Create CIS Profile POST: /cis/customer-profile/v2/internal/customers (No token) Request: {party, profile, contactNumber, email, address, agreement, consent, riskProfile, identity, identifier, channel, classification, BAN**} Action: “CREATE_PROFILE” Response: CISID, partyPrefix, partyFirstName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, classificationType, classificationTypeValue, RMNO, EXTID
216. V2 - CIS_Wrapper (new) : Add Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
217. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=PDPA}/doc-type/{docTypeCode4=PDPA006}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
218. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
219. If CIS returned errors for update PDPA, then end the flow.
220. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete
221. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
222. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID

### Page 13: ETB (FR)_Backup

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. Host Integration for Registration ETB
4. 1. First Page
5. Apigee (Engagement)
6. Apigee (Experience)
7. CIAM (SAAS – no SecureConnect)
8. IAM Proxy (Experience)
9. 2. Welcome Page
10. Defer to MVP0 Check Wifi/Cellular Check SIM Face Liveness check (SDK)
11. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
12. CIAM (SaaS)
13. 3. Accept T&C
14. T&C-MS/DB
15. 4. Input ID & DOB
16. TBC -Combine services
17. - CIS not found - Check DOB
18. 5. Input Laser code
19. (Restful/XML)
20. 6. Display Mobile No.
21. User input phone number in FR
22. 7. Input OTP
23. 8. Consent PDPA
24. PDPA content/DB
25. 9. Introduction for face scan
26. Ask device permission - Camera
27. 10. Face scan
28. FR – No Liveness SDK, only capture face photo send to compare at backend system
29. Cache PPI data (Data TBD)
30. 11. Set up PIN and Reconfirm PIN
31. Create RegistrationRecord
32. Create Customer Prospect Profile Record
33. CIS ID
34. If CIS = Success then start process in Camunda otherwise send failure message.
35. JWT Token (CIS ID)
36. Update Customer Prospect Profile Record
37. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
38. Terminate Stale Processes
39. How to store Digital ID & Device Binding Key. Is it part of PING SDK?
40. 12. Select Product
41. Read the Cache for the Product details
42. 13.Suceess
43. Update RegistrationRecord
44. Control Screen
45. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
46. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
47. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
48. IAM proxy (Experience)
49. APIGee (Experience)
50. APIGee (Engagement)
51. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
52. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
53. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
54. If Active account – Yes Then, check Risk Level, IAL, CT
55. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
56. OPO_04 OPO API detail - TBC
57. Cache Product details
58. CIS ID and Registration Process Instance Key
59. Compare Mobile No. from 2 source If Yes, Send OTP
60. Liveness Check If Yes, do face compare
61. Store DigitalID & DeviceBindingKey in SecureStorage
62. Generate Key call to CIAM
63. E1: Event topic: customer.created
64. E2: Event topic: customer.update
65. SetupPIN (TBD) Request: PIN, SessionID Response: AccessToken, Digital ID, DeviceFingerprintID,
66. Fetch Task
67. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
68. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
69. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
70. OPO_06 OPO API detail - TBC
71. OPO_05 OPO detail – Start Process gRPC Call
72. OPO_07 OPO detail – Submit task gRPC Call
73. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
74. CIAMService-AcceptT&C (TBD) Request: SessionID Response: TBD
75. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
76. FaceComparison (TBD) Request: Picture, SessionID, .. Response: TBD
77. StartOnboardingByCID (TBD) Request: CitizenID, DoB, SessionID Response: TBD
78. AcceptPDPA (TBD) Request: SessionID Response: TBD
79. CIAMService-ValidateCID (TBD) Request: Lazer Code, SessionID Response: TBD
80. Get PDPA content (TBD) Request: ??? Response: ???
81. ValidateMobileNumber(TBD) Request: MobileNo, SessionID Response: TBD
82. VerifyMobileNumber(TBD) Request: OTP, SessionID Response: TBD
83. What’s Language?
84. Get T&C content (TBD) Request: ??? Response: SessionID, ???
85. IAM_01: T&C content Inquiry
86. IAM_02: Customer Search
87. IAM_03: Customer Profile Inquiry
88. IAM_04: Get customer ID Card Info
89. IAM_10: Get PDPA content
90. IAM_11: Update PDPA content
91. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
92. IAM_12: Face Comparison (photo dipchip Template =I01)
93. IAM_05: Check DOPA
94. IAM_06:Check Customer Suspicious Account
95. IAM_08: Send SMS OTP
96. IAM_07: Get Customer Mobile Numbers
97. IAM_09: PDPA consent Inquiry
98. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
99. CIS_01: Customer Search Request: ID, ID Type Response: DoB, RM No. or CIS No., CIS status
100. CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
101. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
102. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
103. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
104. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
105. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
106. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
107. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
108. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
109. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
110. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
111. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
112. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
113. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
114. If Pass, OTP Verification
115. If update PDPA consent fail, ignore and go to next step.
116. If Pass, ID Card Expire
117. If Pass, Mule Account
118. If CIS profile not found or CIS status is invalid, search RM
119. If RM is found, get customer profile from RM
120. If RM is found, get customer account relationship from RM
121. If cache not found, then inquiry C2A from RM.
122. Delete phone number from other profile (if duplicate) -> Broadcast to other systems

### Page 14: ETB (Full)Backup


### Page 15: ETB_Ping

1. Host Integration for Registration ETB
2. 1. First Page
3. 2. Welcome Page
4. Defer to MVP0 Check Wifi/Cellular Check SIM Face Liveness check (SDK)
5. Apigee (Engagement)
6. Apigee (Experience)
7. CIAM (SAAS – no SecureConnect)
8. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
9. 3. Accept T&C
10. T&C-MS/DB
11. Cache per session?? TBC design
12. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
13. 4. Input ID & DOB
14. - CIS not found - Check DOB
15. 5. Input Laser code
16. 6. Display Mobile No.
17. User input phone number in FR
18. 7. Input OTP
19. 8. Consent PDPA
20. PDPA content/DB
21. 9. Introduction for face scan
22. Ask device permission - Camera
23. 10. Face scan
24. If CIS = Success then start process in Camunda otherwise send failure message.
25. FR – No Liveness SDK, only capture face photo send to compare at backend system
26. 11. Set up PIN and Reconfirm PIN
27. Create customer prospect Profile record
28. JWT Token (CIS ID)
29. CIS ID
30. 12. Select Product
31. 13.Suceess
32. Control Screen
33. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
34. APIGee (Experience)
35. APIGee (Engagement)
36. Start ETB Biz Onboarding flow Request: rmNum, mobileNum, Dopa check, Face compare check, Mobile OTP check, T&C version, T&C consent date-time Response: CIS ID
37. If Active account – Yes Then, check Risk Level, IAL, CT
38. A3: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
39. Write to cache
40. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
41. Compare Mobile No. from 2 source If Yes, Send OTP
42. Liveness Check If Yes, do face compare
43. Store DigitalID & DeviceBindingKey in SecureStorage
44. E2: Event topic: customer.update
45. E1: Event topic: customer.created
46. SetupPIN (TBD) Request: PIN, SessionID Response: AccessToken, Digital ID, DeviceFingerprintID,
47. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
48. CIAMService-AcceptT&C (TBD) Request: SessionID Response: TBD
49. AcceptPDPA (TBD) Request: SessionID Response: TBD
50. FaceComparison (TBD) Request: Picture, SessionID, .. Response: TBD
51. StartOnboardingByCID (TBD) Request: CitizenID, DoB, SessionID Response: TBD
52. CIAMService-ValidateCID (TBD) Request: Lazer Code, SessionID Response: TBD
53. Get PDPA content (TBD) Request: ??? Response: ???
54. ValidateMobileNumber(TBD) Request: MobileNo, SessionID Response: TBD
55. VerifyMobileNumber(TBD) Request: OTP, SessionID Response: TBD
56. Get T&C content (TBD) Request: ??? Response: SessionID, ???
57. A1: T&C content Inquiry
58. A10: Get PDPA content
59. A9: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
60. A12: Face Comparison (photo dipchip Template =I01)
61. A5:Check DOPA
62. A6:Check Customer Suspicious Account
63. A8:Send SMS OTP
64. A2: Customer Search Request: ID, ID Type Response: DoB, RM No. or CIS No., CIS status
65. A14: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status (Filter with account status, and relationship)
66. A7:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
67. A13: Create Profile Request: RM No., Mobile Number, IAL= 2.3 Response: CIS ID
68. A15: Add Product to CIS Profile Request: Account Number, Account Type, Flag = Add Response: Result
69. A11: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
70. A4:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
71. If update PDPA consent fail, ignore and go to next step.
72. If Pass, OTP Verification
73. If Pass, ID Card Expire
74. If Pass, Mule Account
75. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
76. If CIS profile not found or CIS status is invalid, search RM
77. If RM is found, get customer profile from RM
78. If RM is found, get customer account relationship from RM
79. If cache not found, then inquiry C2A from RM.
80. Read from cache

### Page 16: ETB (MVP0) Back up 19 Aug

1. Cache per session?? TBC design
2. Header (common) TBC TraceID – send end to end TransRef (Unique per call) Device IP Address
3. Host Integration for Registration ETB
4. 1. First Page
5. 2. Welcome Page
6. CIAM SAAS Connection - Options 1.SAAS -> Apigee(experience)->Apigee(engagement)/Apigee(enterprise) 2.SAAS+SecureConnect ->Apigee(engagement)/Apigee(enterprise) 3.BBLCloud(experience)->Apigee(engagement)/Apigee(enterprise)
7. Defer to MVP2 Face Liveness check (SDK)
8. CIAM (SaaS)
9. Ask Permission for -Activity tracking -Push notification
10. 3. Accept T&C
11. T&C-MS/DB
12. Auth_ID token (10minutes expired)
13. Apigee (Engagement)
14. Apigee (Experience)
15. CIAM (SAAS – no SecureConnect)
16. IAM Proxy (Experience)
17. 4. Input ID & DOB
18. TBC -Combine services
19. 5. Input Laser code
20. (Restful/XML)
21. 6. Display Mobile No.
22. User input phone number, no check sim
23. 7. Input OTP
24. 8. Consent PDPA
25. TBC
26. PDPA content/DB
27. 9. Introduction for face scan
28. Ask Permission for -Camera
29. 10. Face scan
30. FR – No Liveness SDK, only capture face photo send to compare at backend system
31. Cache PPI data (Data TBD)
32. If CIS = Success then start process in Camunda otherwise send failure message.
33. 11. Set up PIN and Reconfirm PIN
34. Create RegistrationRecord
35. Create Customer Prospect Profile Record
36. CIS ID
37. Update Customer Prospect Profile Record
38. JWT Token (CIS ID)
39. Terminate Stale Processes
40. H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
41. Remove this call.
42. 12. Select Product
43. Read the Cache for the Product details
44. Update RegistrationRecord
45. 13.Suceess
46. Control Screen
47. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
48. H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
49. H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
50. IAM proxy (Experience)
51. APIGee (Experience)
52. APIGee (Engagement)
53. OPO_02: Get Customer Account OPO API detail - /opo/registration/gateway/v1/task Request: registProcInsKey Response: products
54. OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
55. OPO_01: Start ETB Biz Onboarding flow OPO API detail – POST: /opo/registration/gateway/v1/process Request: rmNum, mobile-number, onboarding-type, bblIal, idNum, isDopaVerified, isFaceComparisonSuccess, isMobileVerified, termsAndConditionsVersion, termsAndConditionsCOnsentDateTime Response: Cis_id, registProcInsKey
56. CIS_02: Customer Profile Inquiry (for SAAS) Request: RM No. Response: - CT, KYC risk level, KYC risk reason code, BBLIAL - Flag - Has Active Accounts
57. OPO_04 OPO API detail - TBC
58. Parallel Task to onboard TSP, PFM, CDP
59. Cache Product details
60. CIS ID and Registration Process Instance Key
61. Liveness Check If it passes, proceed the Face comparison
62. Generate Key call to CIAM
63. Store DigitalID & DeviceBindingKey
64. E2: Event topic: customer.update
65. E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
66. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, registProcInsKey
67. PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
68. Fetch Task
69. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId
70. CDP1: Create CDP Profile -à TBC POST: xxxxxx Request: CISID Response: xxxxx
71. Call
72. H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
73. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
74. Add product into CIS (TBD) Request: CIS ID, ApplID, Account Num Response: ???
75. OPO_06 OPO API detail - TBC
76. OPO_05 OPO detail – Start Process gRPC Call
77. OPO_07 OPO detail – Submit task gRPC Call
78. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
79. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
80. สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
81. FaceComparison Request: Picture (base64 encoded) Response: PIN callback
82. AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
83. auth ID token – return in every call, change to the new one every call (60 minutes expired)
84. auth ID token in the request
85. CIAMService-ValidatelaserCode Request: laserCode Response: prompt mobileNumber
86. StartProcessByCID Request: citizen ID, DOB Response: citizen ID, DOB, prompt laserCode
87. Get PDPA content (TBD) Request: ??? Response: ???
88. ValidateMobileNumber Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
89. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: PDPA URL
90. CIAM checks 1. Have rmNum 2. cisId = null 3. Validate DOB
91. IAM_16: OPO 01
92. Get T&C content (TBD) Request: ??? Response: SessionID, ???
93. CIAM validates OTP. If it matches, then can proceed further
94. If users already accepted PDPA clause 6, skip to Face verificatoin
95. CIAM checks bblscore. If it equals to 3, then can proceed further
96. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
97. Submit device meta data Request: metadata, location, message Response: T&C URL
98. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
99. System token issued by Ping
100. Review Security with SM if need to go through Apigee Engagement (ADR_15)
101. CIAM checks 1. ctCode = 09 (To-be: check ctCode & idType in MMP) 2. bblIalCode >= 21 3. riskLevel != 3X, 3U, 3V, 3A, 3B 4. hasActiveAccount = Y Then, can proceed further
102. CIAM checks ID card expired date, allow to continue if expired date is today
103. Private API - Group System token issued by Camunda
104. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
105. IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
106. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, tandCUrl
107. IAM_03: Customer Profile Inquiry (To-be: IAM_13) Request: rmNum Response: rmNum, ctCode, nationality, riskLevel, riskLevelReasonCode, bblIalCode, hasActiveAccount
108. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
109. IAM_11: Update PDPA consent (To-be: IAM_18)
110. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
111. CIS_05: PDPA Consent Inquiry (Clause 6) Request: ID, ID Type Response: Purpose Code, Purpose Flag (for Clause 6 only)
112. IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
113. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg
114. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
115. IAM_08: Send SMS OTP Request: mobileNum Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0
116. IAM_07: Get Customer Mobile Numbers (To-be: IAM_14)
117. IAM_09: PDPA consent Inquiry Request: idNum Response: purposeCode, purposeFlag
118. H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
119. CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
120. CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
121. CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
122. CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
123. H5: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
124. CIS_04:Get Customer Mobile Numbers Request: RM No. Response: mobileNumberList (90-97, 99)
125. CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
126. CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
127. CIS_07: Create Profile Request: contactNumber, diallingCountryCode, identifierTypeValue (RM), partyCertificateType, partyCertificateTypeValue, bblIal, partyAgreement, partyAgreementDate, partyAgreementExpiry, partyAgreementExtendedData, partyAgreementVersion, partyAgreementHash Response: CIS ID
128. CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
129. CIS_03:Get Customer ID Card Info Request: CitizenID Response: ID expiry date, First name, Last name, Title
130. H2: Customer Profile Inquiry POST:/esis/customer-services/customers/profile/ Request: RM No. Response: Risk Rating, IAL, firstname, lastname
131. H4: RequestIdentityInfo POST:/smartcard/echannel/identity/inquiry Request: CitizenID Response: ID expiry date, ID, First name, Last name
132. H6: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
133. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
134. H3: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID) Response: Account Num, relationshipCode, accountStatus
135. H7: CustomerProfileContactInfoInqService POST:/esis/customer-services/customers/contact-numbers/mobile/inquiry Request: RM No. Response: mobileNumberList
136. H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
137. If CIS returned errors for update PDPA, then end the flow.
138. If CIS profile not found or CIS status is invalid, search RM
139. If RM is found, get customer profile from RM
140. If RM is found, get customer account relationship from RM
141. If cache not found, then inquiry C2A from RM.
142. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
143. CIAM token in the API request (1st call)

## Optional Branches

- If CIS = Success then start process in Camunda otherwise send failure message.
- If API update CustomerProfileRelAdd fail
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- Retry 3 times
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- Liveness Check If it passes, proceed the Face comparison
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If cache not found, then inquiry C2A from RM.
- If RM is found, get customer account relationship from RM
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- If RM is found, get customer profile from RM
- [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- [CIAM checks] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_04 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [CIAM checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
- [CIAM checks] If customer idType = CI, Continue to IAM_04 Else, Skip IAM_04 and IAM05 Continue at IAM_06 IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
- [CIAM checks] ID card expired date, allow to continue if expired date is today
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Retry 3 times
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType != ‘CI’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Remark: If Fail to Create TSP Profile, OPO will not retry
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If CIS returned errors for update PDPA, then end the flow.
- If cache not found, then inquiry C2A from RM.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- [CIAM validate] - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error
- [AuditLog] in case Fail Only Inquiry wrapper – No token
- [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response ETB with MB or NA - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM checks] If ETB with IA Profile response state ETB_FC If ETB without IA Profile response state ETB_NP_FC If ETB_MB response state ETB_MB_FC
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2.1 - 1-4 Face Invalid attempts for ETB with NA - In flow error Response 9.2.2 - 1-4 Face Invalid attempts for ETB with NA and CIAM profile is missing - In flow error Response 9.2.3 - 1-4 Face Invalid attempts for ETB with MB - End flow - Customized error - End flow - OOTB error
- Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- If found duplicate Email
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Retry 3 times
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- If enroll TSP (above step) fail
- 12. Select Product Remark: - Sorting by using card type: 1.) AMEX, 2.) JCB, 3.) VISA, 4.) Master and 5.) UnionPay - Sorting of each card type by using BIN no. (ascending order) - If no image for render in cc, please use “Placeholder-Landscape-Content” Only - If no image for render in ST/IM, please use “Placeholder” Only
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- If Fail, then make pendingRegisterFlag is true
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
- CIAM Checks If msgDecision = “A” proceed next step Else return error
- If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
- Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
- Liveness Check If it passes, proceed the Face comparison
- Mapping Field to existing OPO response format. If appId is “CH”, then map - accountDisplayName = cardName - category is “Cards” / “บัตรต่าง ๆ” (depend on language) - accountNumber is accountNum - displayAccountNumber is maskedCardNum - productCode is productCode - order same as response from DEH Else If appId is “ST”or “IM”, then map - accountDisplayName = accountType of DEH (meaning to accountTypeValue of CIS) - category is “Deposit Accounts” / “บัญชีเงินฝาก” (depend on language) - accountNumber is accountNum - displayAccountNumber is “xxx-x-xx” + last 4 digits of accountNum - accountType is accountType - order same as response from DEH
- 1. Setup imageURL: If appId is “CH”, then send “/Products/CC/{productCode}-Content” Else If appId is “ST” or “IM”, then send “/Products/BB/{accountDisplayName}” 2. Setup defaultImageUrl If appId is “CH”, then send “/Products/CC/Placeholder-Landscape-Content”. Else If appId is “ST” or “IM”, then send “/Products/BB/Placeholder”.
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- IAM_16 v.2: ETB Create Customer Profile CIAM condition - If bblTalCode from IAM26 == "23", sends bblTalUpdatedDatetime that retrieved from IAM26 - else if bblTalCode from IAM26 != "23", sends bblTalUpdatedDatetime that users do the face scan. Request: regType, user, termAndConditions, pdpaConsents - regType is used to separate between ETB and ETB with MB Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
- If CIS returned errors for update T&C, then end the flow.
- If CIS returned errors for update PDPA, then end the flow.
- If profileOption = WithCondition and appId = CH then not return account with puchasing and corporate card (accountNum starts with '[MASKED_CODE]' or '[MASKED_CODE]')
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- [CIAM validate] - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error
- [AuditLog] in case Fail Only Inquiry wrapper – No token
- [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response ETB with MB or NA - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM checks] If ETB with IA Profile response state ETB_FC If ETB without IA Profile response state ETB_NP_FC If ETB_MB response state ETB_MB_FC
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2.1 - 1-4 Face Invalid attempts for ETB with NA - In flow error Response 9.2.2 - 1-4 Face Invalid attempts for ETB with NA and CIAM profile is missing - In flow error Response 9.2.3 - 1-4 Face Invalid attempts for ETB with MB - End flow - Customized error - End flow - OOTB error
- Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- If found duplicate Email
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Retry 3 times
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- If enroll TSP (above step) fail
- 12. Select Product Remark: - Sorting by using card type: 1.) AMEX, 2.) JCB, 3.) VISA, 4.) Master and 5.) UnionPay - Sorting of each card type by using BIN no. (ascending order) - If no image for render in cc, please use “Placeholder-Landscape-Content” Only - If no image for render in ST/IM, please use “Placeholder” Only
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- If Fail, then make pendingRegisterFlag is true
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
- CIAM Checks If msgDecision = “A” proceed next step Else return error
- If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
- Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
- Liveness Check If it passes, proceed the Face comparison
- Mapping Field to existing OPO response format. If appId is “CH”, then map - accountDisplayName = cardName - category is “Cards” / “บัตรต่าง ๆ” (depend on language) - accountNumber is accountNum - displayAccountNumber is maskedCardNum - productCode is productCode - order same as response from DEH Else If appId is “ST”or “IM”, then map - accountDisplayName = accountType of DEH (meaning to accountTypeValue of CIS) - category is “Deposit Accounts” / “บัญชีเงินฝาก” (depend on language) - accountNumber is accountNum - displayAccountNumber is “xxx-x-xx” + last 4 digits of accountNum - accountType is accountType - order same as response from DEH
- 1. Setup imageURL: If appId is “CH”, then send “/Products/CC/{productCode}-Content” Else If appId is “ST” or “IM”, then send “/Products/BB/{accountDisplayName}” 2. Setup defaultImageUrl If appId is “CH”, then send “/Products/CC/Placeholder-Landscape-Content”. Else If appId is “ST” or “IM”, then send “/Products/BB/Placeholder”.
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- IAM_16 v.2: ETB Create Customer Profile CIAM condition - If bblTalCode from IAM26 == "23", sends bblTalUpdatedDatetime that retrieved from IAM26 - else if bblTalCode from IAM26 != "23", sends bblTalUpdatedDatetime that users do the face scan. Request: regType, user, termAndConditions, pdpaConsents - regType is used to separate between ETB and ETB with MB Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
- If CIS returned errors for update T&C, then end the flow.
- If CIS returned errors for update PDPA, then end the flow.
- If profileOption = WithCondition and appId = CH then not return account with puchasing and corporate card (accountNum starts with '[MASKED_CODE]' or '[MASKED_CODE]')
- If CIS = Success then start process in Camunda otherwise send failure message.
- If API update CustomerProfileRelAdd fail
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- If Active account – Yes Then, check Risk Level, IAL, CT
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- Compare Mobile No. from 2 source If Yes, Send OTP
- Liveness Check If Yes, do face compare
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- If Pass, OTP Verification
- If update PDPA consent fail, ignore and go to next step.
- If Pass, ID Card Expire
- If Pass, Mule Account
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- [Checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- [Checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
- [Checks #3] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_04 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- [Validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- Check If Mobile number is in RM profile, Send OTP if pass
- Display PDPA screen if user haven’t given consent.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, and DOB is correct, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM
- Check Risk Rating and IAL If Pass, get ID card information
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS = Success then start process in Camunda otherwise send failure message.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If cache not found, then inquiry C2A from RM.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- If RM is found, get customer profile from RM
- [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- [CIAM checks] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_05 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [AuditLog] in case Fail Only Inquiry wrapper – No token
- [AuditLog] in case Fail Only Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - End flow - Customized error - End flow - OOTB error
- [CIAM checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
- [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response (ETB with MB or NA) - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Retry 3 times
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error If pass above dob validation then check - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’ and has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
- CIAM checks if there is no Missing_IDM_Profile flag in nodeState, call IAM_31 Else call IAM_15
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- IAM_31: ETB Create Customer Profile Request: customerProfile, contactInfo, termAndConditions, pdpaConsents, ... Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
- If CIS returned errors for update PDPA, then end the flow.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- If Active account – Yes Then, check Risk Level, IAL, CT
- Compare Mobile No. from 2 source If Yes, Send OTP
- Liveness Check If Yes, do face compare
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- If Pass, OTP Verification
- If update PDPA consent fail, ignore and go to next step.
- If Pass, ID Card Expire
- If Pass, Mule Account
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- If Active account – Yes Then, check Risk Level, IAL, CT
- Compare Mobile No. from 2 source If Yes, Send OTP
- Liveness Check If Yes, do face compare
- If update PDPA consent fail, ignore and go to next step.
- If Pass, OTP Verification
- If Pass, ID Card Expire
- If Pass, Mule Account
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Liveness Check If it passes, proceed the Face comparison
- สรุป - เรายัง 24x7 หรือไม่? – RM ปิด 2:30-3:00 - ตอน RM ปิด จะสามารถ Inq Account List ได้หรือไม่? – RM ปิด 2:30-3:00 Option 1. ปิดตามเวลา 2. ปล่อย Error - โชว์ Message หน้าจอ ตามที่กำหนดเหมือนกันทั้งปิดระบบกับล่ม à เลือก Option2
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems

## Decision Points

- If CIS = Success then start process in Camunda otherwise send failure message.
- If API update CustomerProfileRelAdd fail
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- Retry 3 times
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- CIS_08: Get Customer Account Relationship /cis/v1/customers-accounts/inquiry/account Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If cache not found, then inquiry C2A from RM.
- If RM is found, get customer account relationship from RM
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- V1 - CIS_01: Customer Search by Citizen ID POST: /cis/v1/customer-onboarding/inquiry/profile Request: idNum Response: DoB, RM No. or CIS No., CIS status V2 - CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- If RM is found, get customer profile from RM
- [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
- [CIAM checks] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_04 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [CIAM checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
- [CIAM checks] If customer idType = CI, Continue to IAM_04 Else, Skip IAM_04 and IAM05 Continue at IAM_06 IAM_04: Get customer ID Card Info Request: idNum Response: expiryDate, idNum, titleNameTh firstNameTh, lastNameTh, titleNameEn firstNameEn, lastNameEn
- [CIAM checks] ID card expired date, allow to continue if expired date is today
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- [CIAM checks] result: contains only “dateTime” and no “suspiciousCustomerInfo” Then, can proceed further
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Retry 3 times
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType != ‘CI’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Remark: If Fail to Create TSP Profile, OPO will not retry
- V1 - CIS_08: Get Customer Account Relationship POST: /cis/v1/customers-accounts/inquiry/account Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship) V2 - CIS_Wrapper (8): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType =R06/R23 , idNumber= Nationality+idNumber, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- V1 - CIS_06: Update PDPA consent POST: /cis/v1/customer-onboarding/core/pdpa Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status V2 - CIS_Wrapper (6): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
- V1 - CIS_09: Add Product to CIS Profile POST: /cis/v1/customers-accounts/customers/accounts Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status V2 - CIS_Wrapper (new) : Add or Update Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If cache not found, then inquiry C2A from RM.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: identityType, identityValue, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob, cisExternalId
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- [CIAM validate] - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
- CIS_Wrapper(4): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan, customerIdentity}, tellerId, photoFlag, dailyFalg, dataTypeFlag Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code
- [AuditLog] in case Fail Only Inquiry wrapper – No token
- [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response ETB with MB or NA - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
- IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM checks] If ETB with IA Profile response state ETB_FC If ETB without IA Profile response state ETB_NP_FC If ETB_MB response state ETB_MB_FC
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2.1 - 1-4 Face Invalid attempts for ETB with NA - In flow error Response 9.2.2 - 1-4 Face Invalid attempts for ETB with NA and CIAM profile is missing - In flow error Response 9.2.3 - 1-4 Face Invalid attempts for ETB with MB - End flow - Customized error - End flow - OOTB error
- Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- IAM_38: EFM Request Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
- IAM_15 : Reactivation Update T&C Request: cisId, partyAgreementDateTime, partyAgreementVersion, partyAgreementHash, agreementType, agreementTypeValue Action: UPDATE_AGREEMENT Response: Status
- CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- CIS_Wrapper(4) : Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- If found duplicate Email
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Retry 3 times
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- If enroll TSP (above step) fail
- 12. Select Product Remark: - Sorting by using card type: 1.) AMEX, 2.) JCB, 3.) VISA, 4.) Master and 5.) UnionPay - Sorting of each card type by using BIN no. (ascending order) - If no image for render in cc, please use “Placeholder-Landscape-Content” Only - If no image for render in ST/IM, please use “Placeholder” Only
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- If Fail, then make pendingRegisterFlag is true
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
- CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship}, with appId = [ST,CH] and profileOption = “WithCondition” Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type, ownershipCode
- IAM_11v2: Update PDPA consent Request: idType, idNumber, titleName, firstName, lastName, dob, nationality, consentdate, brCode, channel, purposeCode, purposeFlag - Action: UPDATE_PDPA Response: status
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
- Register Device Notification Request: appId = ‘na’, cisId ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- CIAM Checks If msgDecision = “A” proceed next step Else return error
- Filter -Not allowed account status -Filter card already linked
- If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
- Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- GET [MASKED_URL] Header: bbl-cust-id-token, accept-language, bbl-channel, Content-Type Response: Account Type, Account Number, Account Status, Masked card number (with last 4 digit and return CC only), Card reference number (return CC only), Card name (return CC only), Product Code (return CC only), appId
- Mapping Field to existing OPO response format. If appId is “CH”, then map - accountDisplayName = cardName - category is “Cards” / “บัตรต่าง ๆ” (depend on language) - accountNumber is accountNum - displayAccountNumber is maskedCardNum - productCode is productCode - order same as response from DEH Else If appId is “ST”or “IM”, then map - accountDisplayName = accountType of DEH (meaning to accountTypeValue of CIS) - category is “Deposit Accounts” / “บัญชีเงินฝาก” (depend on language) - accountNumber is accountNum - displayAccountNumber is “xxx-x-xx” + last 4 digits of accountNum - accountType is accountType - order same as response from DEH
- 1. Setup imageURL: If appId is “CH”, then send “/Products/CC/{productCode}-Content” Else If appId is “ST” or “IM”, then send “/Products/BB/{accountDisplayName}” 2. Setup defaultImageUrl If appId is “CH”, then send “/Products/CC/Placeholder-Landscape-Content”. Else If appId is “ST” or “IM”, then send “/Products/BB/Placeholder”.
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- IAM_20: Face Comparison Request: idNum, requestType = R06/R23, imageFile = string(base64), imageSourceType=I03, requestId = NCIA+transaction ID, requestChannel = NCIA, … idNum - Thai: idNum - Foreigner: nationality|idNum Response: status, requestId, Confidencescore, bblscore
- IAM_16 v.2: ETB Create Customer Profile CIAM condition - If bblTalCode from IAM26 == "23", sends bblTalUpdatedDatetime that retrieved from IAM26 - else if bblTalCode from IAM26 != "23", sends bblTalUpdatedDatetime that users do the face scan. Request: regType, user, termAndConditions, pdpaConsents - regType is used to separate between ETB and ETB with MB Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
- V2 - CIS_Wrapper (16): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
- CIS_Wrapper (12) : Add Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update T&C, then end the flow.
- If CIS returned errors for update PDPA, then end the flow.
- If profileOption = WithCondition and appId = CH then not return account with puchasing and corporate card (accountNum starts with '[MASKED_CODE]' or '[MASKED_CODE]')
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: identityType, identityValue, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob, cisExternalId
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- [CIAM validate] - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
- CIS_Wrapper(4) Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan, customerIdentity}, tellerId, photoFlag, dailyFalg, dataTypeFlag Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code
- [AuditLog] in case Fail Only Inquiry wrapper – No token
- [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response ETB with MB or NA - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
- IAM_37: EFM Advice Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM checks] If ETB with IA Profile response state ETB_FC If ETB without IA Profile response state ETB_NP_FC If ETB_MB response state ETB_MB_FC
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2.1 - 1-4 Face Invalid attempts for ETB with NA - In flow error Response 9.2.2 - 1-4 Face Invalid attempts for ETB with NA and CIAM profile is missing - In flow error Response 9.2.3 - 1-4 Face Invalid attempts for ETB with MB - End flow - Customized error - End flow - OOTB error
- Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- IAM_38: EFM Request Request: userSessionId, userNum, userEmail, userPhone, userFirstLogonDateTime, userOpenDate, msgType, msgChannel, … Response: status
- IAM_15 : Reactivation Update T&C Request: cisId, partyAgreementDateTime, partyAgreementVersion, partyAgreementHash, agreementType, agreementTypeValue Action: UPDATE_AGREEMENT Response: Status
- CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- CIS_Wrapper(4): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- If found duplicate Email
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Retry 3 times
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- If enroll TSP (above step) fail
- 12. Select Product Remark: - Sorting by using card type: 1.) AMEX, 2.) JCB, 3.) VISA, 4.) Master and 5.) UnionPay - Sorting of each card type by using BIN no. (ascending order) - If no image for render in cc, please use “Placeholder-Landscape-Content” Only - If no image for render in ST/IM, please use “Placeholder” Only
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- If Fail, then make pendingRegisterFlag is true
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
- CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- CIS_Wrapper (10): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship}, with appId = [ST,CH] and profileOption = “WithCondition” Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type, ownershipCode
- IAM_11v2: Update PDPA consent Request: idType, idNumber, titleName, firstName, lastName, dob, nationality, consentdate, brCode, channel, purposeCode, purposeFlag - Action: UPDATE_PDPA Response: status
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
- Register Device Notification Request: appId = ‘na’, cisId ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- CIAM Checks If msgDecision = “A” proceed next step Else return error
- Filter -Not allowed account status -Filter card already linked
- If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
- Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- GET [MASKED_URL] Header: bbl-cust-id-token, accept-language, bbl-channel, Content-Type Response: Account Type, Account Number, Account Status, Masked card number (with last 4 digit and return CC only), Card reference number (return CC only), Card name (return CC only), Product Code (return CC only), appId
- Mapping Field to existing OPO response format. If appId is “CH”, then map - accountDisplayName = cardName - category is “Cards” / “บัตรต่าง ๆ” (depend on language) - accountNumber is accountNum - displayAccountNumber is maskedCardNum - productCode is productCode - order same as response from DEH Else If appId is “ST”or “IM”, then map - accountDisplayName = accountType of DEH (meaning to accountTypeValue of CIS) - category is “Deposit Accounts” / “บัญชีเงินฝาก” (depend on language) - accountNumber is accountNum - displayAccountNumber is “xxx-x-xx” + last 4 digits of accountNum - accountType is accountType - order same as response from DEH
- 1. Setup imageURL: If appId is “CH”, then send “/Products/CC/{productCode}-Content” Else If appId is “ST” or “IM”, then send “/Products/BB/{accountDisplayName}” 2. Setup defaultImageUrl If appId is “CH”, then send “/Products/CC/Placeholder-Landscape-Content”. Else If appId is “ST” or “IM”, then send “/Products/BB/Placeholder”.
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- IAM_20: Face Comparison Request: idNum, requestType = R06/R23, imageFile = string(base64), imageSourceType=I03, requestId = NCIA+transaction ID, requestChannel = NCIA, … idNum - Thai: idNum - Foreigner: nationality|idNum Response: status, requestId, Confidencescore, bblscore
- IAM_16 v.2: ETB Create Customer Profile CIAM condition - If bblTalCode from IAM26 == "23", sends bblTalUpdatedDatetime that retrieved from IAM26 - else if bblTalCode from IAM26 != "23", sends bblTalUpdatedDatetime that users do the face scan. Request: regType, user, termAndConditions, pdpaConsents - regType is used to separate between ETB and ETB with MB Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
- CIS_Wrapper (16): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
- CIS_Wrapper (12) : Add Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update T&C, then end the flow.
- If CIS returned errors for update PDPA, then end the flow.
- If profileOption = WithCondition and appId = CH then not return account with puchasing and corporate card (accountNum starts with '[MASKED_CODE]' or '[MASKED_CODE]')
- If CIS = Success then start process in Camunda otherwise send failure message.
- If API update CustomerProfileRelAdd fail
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- If Active account – Yes Then, check Risk Level, IAL, CT
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- Compare Mobile No. from 2 source If Yes, Send OTP
- Liveness Check If Yes, do face compare
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If Pass, OTP Verification
- If update PDPA consent fail, ignore and go to next step.
- If Pass, ID Card Expire
- If Pass, Mule Account
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- After clicking Sign up, then check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
- [Checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- [Checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
- [Checks #3] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_04 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- (NEW) H22: Request For Approve Transaction
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- [Validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- Check If Mobile number is in RM profile, Send OTP if pass
- Display PDPA screen if user haven’t given consent.
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, and DOB is correct, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM
- Check Risk Rating and IAL If Pass, get ID card information
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS = Success then start process in Camunda otherwise send failure message.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- V1 - CIS_06: Update PDPA consent POST: /cis/v1/customer-onboarding/core/pdpa Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status V2 - CIS_Wrapper (6): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
- H9: PDPAConsentInq POST: /PDPA/consent/inquiry Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST: /PDPA/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add or update account (if already added in CIS)
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST: /cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMoD PUT: /esis/customer-services/customers/profiles/ial Request: RM no., IAL Info Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIAM checks ID card expired date, allow to continue if expired date is today
- V1 - CIS_01: Customer Search by Citizen ID POST: /cis/v1/customer-onboarding/inquiry/profile Request: idNum Response: DoB, RM No. or CIS No., CIS status V2 - CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- V1 - CIS_08: Get Customer Account Relationship POST: /cis/v1/customers-accounts/inquiry/account Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship) V2 - CIS_Wrapper (8): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- V1 - CIS_09: Add Product to CIS Profile POST: /cis/v1/customers-accounts/customers/accounts Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status V2 - CIS_Wrapper (new) : Add or Update Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_OR_UPDATE_ACCOUNT” Response: status
- CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If cache not found, then inquiry C2A from RM.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- V2 - CIS_Wrapper (1): Customer Search by Citizen ID POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelType, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- - Check sum and format of Citizen ID - If customer send information by Tab ‘Thai’ then send idType = ‘CI’ Tab ‘Foreigner’ then send idType = ‘PP’ Tab ‘Alien ID’ then send idType = ‘AI’ Tab ‘Others’ then send idType = ‘OI’
- If RM is found, get customer profile from RM
- [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- H19: BBLOwnCustCheckInq Request: ID Type, ID Number, ProfileOption=Full Response: Risk Level, Risk Reason Code, IAL, First name, Last name, Mobile, Profile status, Channel Status, CT Code, RM, first Contact Date, Nationalities1-3, DOB, Occupation, Education, Income, Risk Occupation 1-3, Earning Country 1-3, Place of Birth
- [CIAM checks] Compare MobileNo. in session with mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *If isDisplayMB = N and isDisplayNA = Y , proceed to call IAM_05 *Else if isDisplayMB = Y and isDisplayNA = N then Display screen “Direct to MB” *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- [AuditLog] in case Fail Only Inquiry wrapper – No token
- [AuditLog] in case Fail Only Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - End flow - Customized error - End flow - OOTB error
- [CIAM checks #2] 1. Check ctCode = 09 If true, Continue to Call CustomerProfileContactInfoInqService Else if false, Set isDisplayNA = N and skip call CustomerProfileContactInfoInqService then mapping response to screen
- [ActivityLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response (ETB with MB or NA) - Response 4 - Response Customer Automatically redirected to MB - Response 4 - Response Customer automatically redirected ETB/NA - In flow error Response 4.1 - ETB or Reactivation 1-10 Failed DOB Attempts - In flow error Response 4.2 - ETB or Reactivation 1-10 Failed mobile number Attempts - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM checks] If customer idType = CI, Continue to IAM_05 Else, Skip IAM05 Continue at IAM_06
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- [CIAM checks] code = 0 and desc = สถานะปกติThen, can proceed further *User can retry up to 5 times
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- [ActivityLog] Step 5.1 - ETB Onboarding - Register With NA Laser Code - Response 5.1 - Response with OTP - In flow error Response 5.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 9 - ETB Onboarding - Selfie picture - Response 9.1 - Response with PIN - In flow error Response 9.2 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- CIS_Wrapper() (new): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If found duplicate mobile no.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Retry 3 times
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error If pass above dob validation then check - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’ and has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Create CIS Profile” For other field map below field from CIS Wrapper8 Response by condition below If IDType = ‘CI’ then userDetails/firstName = data.partyFirstName userDetails/middleName​ = data.partyPrefix userDetails/lastName = data.partyLastName userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefixEn userDetails/otherLanguageDetails/firstName​ = data.partyFirstNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = data.partyLastNameEn Else if IDType = ‘PP’ then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/salutation = data.partyPrefix userDetails/otherLanguageDetails/firstName​ = data.partyFirstName userDetails/otherLanguageDetails/middleName =​ data.partyMidName userDetails/otherLanguageDetails/lastName​ = data.partyLastName Else, then userDetails/firstName = “NA” userDetails/middleName​ = “NA” userDetails/lastName = “NA” userDetails/salutation = “NA” userDetails/userID = CIS ID userDetails/customerId = CIS ID userDetails/otherLanguageDetails/firstName​ = data.partyFullNameEn userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = “” Remark: If Fail to Create TSP Profile, OPO will not retry
- V2 - CIS_Wrapper (8): Get Customer Account Relationship POST: /cis/customer-profile/v2/customers/inquiry (with token) Request: CISID, {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- CIAM checks if there is no Missing_IDM_Profile flag in nodeState, call IAM_31 Else call IAM_15
- IAM_11v2: Update PDPA consent Request: idType, idNumber, titleName, firstName, lastName, dob, nationality, consentdate, brCode, channel, purposeCode, purposeFlag - Action: UPDATE_PDPA Response: status
- Verify if accounts sent in the request, presented in RM If any account is not in RM list, then return error Verify account ctCode and account customer ctCode is match for ST, IM account If ctCode is not match, then return error Calculate AccountType and AccountType value if not sent in the request Proceed to add account
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Register Device Notification Request: appId = ‘na’, cisId ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_31: ETB Create Customer Profile Request: customerProfile, contactInfo, termAndConditions, pdpaConsents, ... Response: cisId, processInstancekey, cisExternalId If CIAM does not receive cisId, end the flow
- IAM_20: Face Comparison Request: idNum, requestType = R06/R23, imageFile = string(base64), imageSourceType=I03, requestId = NCIA+transaction ID, requestChannel = NCIA, … idNum - Thai: idNum - Foreigner: nationality|idNum Response: status, requestId, Confidencescore, bblscore
- V2 - CIS_Wrapper (6): Update PDPA consent POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: ID Type, ID Number, cisId Action: “UPDATE_PDPA” Response: Status
- V2 - CIS_Wrapper (new) : Add Account POST: /cis/customer-profile/v2/customers/details (with token) Request: cisId, {account} Action: “ADD_ACCOUNT” Response: status
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- If Active account – Yes Then, check Risk Level, IAL, CT
- Compare Mobile No. from 2 source If Yes, Send OTP
- Liveness Check If Yes, do face compare
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIS_01: Customer Search Request: ID, ID Type Response: DoB, RM No. or CIS No., CIS status
- CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If Pass, OTP Verification
- If update PDPA consent fail, ignore and go to next step.
- If Pass, ID Card Expire
- If Pass, Mule Account
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- If Active account – Yes Then, check Risk Level, IAL, CT
- Compare Mobile No. from 2 source If Yes, Send OTP
- Liveness Check If Yes, do face compare
- A2: Customer Search Request: ID, ID Type Response: DoB, RM No. or CIS No., CIS status
- A14: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status (Filter with account status, and relationship)
- A15: Add Product to CIS Profile Request: Account Number, Account Type, Flag = Add Response: Result
- A11: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- If update PDPA consent fail, ignore and go to next step.
- If Pass, OTP Verification
- If Pass, ID Card Expire
- If Pass, Mule Account
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- If CIS = Success then start process in Camunda otherwise send failure message.
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- H10: PDPAConsentUpdate POST:'/PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent Response: Status, ErrorCode, ErrorDescription
- H9: PDPAConsentInq Request: IdType, IdNumber, Channel Response: Status, IdType, IdNumber, ConsentDate, Channel, FlagNoSign, PurposeCustomerConsent, ErrorCode, ErrorDescription
- Liveness Check If it passes, proceed the Face comparison
- H12: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum Response: status, result
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- AcceptPDPA Request: Approve to accept Response: prompt Picture (base64 encoded)
- CIAM validates OTP. If it matches, then can proceed further
- If users already accepted PDPA clause 6, skip to Face verificatoin
- CIAM checks bblscore. If it equals to 3, then can proceed further
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Review Security with SM if need to go through Apigee Engagement (ADR_15)
- CIAM checks ID card expired date, allow to continue if expired date is today
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- IAM_12: Face Comparison Request: requestType = R06, ImageSourceType1=I03, requestId = NCIA+transaction ID, requestChannel = NCIA Response: Status, RequestId, Confidencescore, bblscore
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- H8: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- CIAM checks code = 0 and desc = สถานะปกติ. Then, can proceed further *User can retry up to 5 times
- CIS_01: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- CIS_08: Get Customer Account Relationship Request: CIS ID, Account Type Response: Account Number, Account status, acctControl1, acctControl2, acctControl3, acctControl4 (Filter with account status, and relationship)
- CIAM compares Mobile No., If matches, Send OTP *User can retry up to 5 times
- CIS_09: Add Product to CIS Profile Request: cisId, accountNumber, accountType, appId, accountOperation, acctControl1, acctControl2, acctControl3, acctControl4 Response: status
- CIS_06: Update PDPA consent Request: ID Type, ID Number, Purpose code, Purpose flag, consent date Response: Status
- CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H11: FaceRegconitionCompare POST:/smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1, RequestId, RequestChannel Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- If CIS returned errors for update PDPA, then end the flow.
- If CIS profile not found or CIS status is invalid, search RM
- If RM is found, get customer profile from RM
- If RM is found, get customer account relationship from RM
- If cache not found, then inquiry C2A from RM.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems

## Success Markers

- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - POST /opo/onboarding/customers/v1/etb/registration Request: products Response: Success/Failure
- E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E6: Publish Event Event topic: <env>.cis.update.customer.success EventType: ADD_ACCOUNT
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
- E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If CIS = Success then start process in Camunda otherwise send failure message.
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- OPO_03: Add Account to CIS OPO API detail - POST /opo/onboarding/customers/v1/etb/registration Request: products Response: Success/Failure
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- Onboarding Success
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If CIS = Success then start process in Camunda otherwise send failure message.
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- 13. Onboarding Success
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
- ETB_OPO_EXP_02 - Submit Products V2 (New Version) OPO API detail - POST /opo/onboarding/customers/etb/v2/registration/accounts/relationship Request: accountNumber Response: Success/Failure
- If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
- Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [CIAM checks #1] 1. ctCode = 09, 52, 11 If not, then Return Error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus =F and - mobileNo. Match with mobileNumberList From H7 Response where seqNum = 90 If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N 5. Check NA is available - MobileNo. in session with any mobile no. in mobileNumberList From H7 Response If match, then Set isDisplayNA = Y Else, isDisplayNA = N *if isDisplayMB = N and isDisplayNA = Y then Display input Laser code screen *else if isDisplayMB = Y and isDisplayNA = N Dthen isplay screen#6 (screen “Direct to MB”) *Else if isDisplayMB = N and isDisplayNA = N then allow user to retry with below condition - 10 retries allowed without restriction. - 11th attempt onward, if no option is available, wait 10 minutes before next retry - 20th attempt, retry is limited for a day *Else if isDisplayMB = Y and isDisplayNA = Y then Display both option on screen
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- CIS_Wrapper (8): UpdateCustomerAgreements POST: /cis/customer-profile/v2/internal/customers/details (No token) Request: cisId, agreement name, agreement accept date, agreementVersion, agreementHash, agreementExpiry (optional), agreementExtendedData (optional) Action: UPDATE_AGREEMENT Response: Status update success/ fail
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- Onboarding Success
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If CIS = Success then start process in Camunda otherwise send failure message.
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- 13. Onboarding Success
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- If “H19: BBLOwnCustCheckInq” success, then Cache partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn.
- ETB_OPO_EXP_02 - Submit Products V2 (New Version) OPO API detail - POST /opo/onboarding/customers/etb/v2/registration/accounts/relationship Request: accountNumber Response: Success/Failure
- If “H21: Get Daily Total Limit” success, then Cache segmentLevel.
- Get enroll TSP status from OPO DB. If get enroll TSP status is success, then Get segmentLevel, partyPrefix, partyFirstName, partyMidName, partyLastName, partyPrefixEn, partyFirstNameEn, partyLastNameEn, partyFullNameEn from cache.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E6: Publish Event Event topic: <env>.cis.update.customer.success EventType: ADD_ACCOUNT
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- If Pass, OTP Verification
- If Pass, ID Card Expire
- If Pass, Mule Account
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- CDP3: Update onboard success
- E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- After clicking Sign up, then check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [Checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- [Validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Check If Mobile number is in RM profile, Send OTP if pass
- Check Risk Rating and IAL If Pass, get ID card information
- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- If CIS = Success then start process in Camunda otherwise send failure message.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [CIAM checks #1] 1. ctCode = 09, 52, 11 otherwise return error 2. Check bblIalCode If ctCode = 09 then bblIalCode >= 21 If result = false, return error Else, Check ID expiry date < Today, return error Else bblIalCode >= 13 If result = false, return error Else, Continue check If Passport expiry date < Today, return error If, KYC Next Due date < Today, return error 3. riskLevel != 3X, 3U, 3V, 3A, 3B In case result = false, return error 4. Check MB option is available - channelStatus = A and - profileStatus=F and - mobile Match with MobileNo. in session If pass all condition then Set isDisplayMB = Y Else, isDisplayMB = N Continue to next process [CIAM checks #2]
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NULL:transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘LaserCode’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScan’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NULL NCBD registration date : NULL Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1: Need EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | IA Cust Error Code: transaction fail Response:
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel that max dailyTotalLitmit of “H21:Get Daily Total Limit” for create CIS profile. Otherwise, return error.
- Create CustomerProfile, CIS ID If success, then proceed to next step. Else, return error at this point
- If CIS = Success then start process in Camunda otherwise send failure message.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionid CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPINandCreateCIS’ TransactionSubType = ‘ETB_NONMB’: transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] Step1: ETB Registration - Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step2: ETB Registration - Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- [AuditLog] Step3: ETB Registration - Enroll Customer profile to TSP Response1: Success Enroll Customer profile to TSP Response2: Fail
- [ActivityLog] Step4: ETB Registration - Enroll Customer profile to TSP Response1: Success (Log Leve2) Response2: Fail (Log Level1)
- 13. Onboarding Success
- [AuditLog] in case Success/Fail Step5: ETB Registration – Add Account to CIS Response1: Success Add Account to CIS Response2: Fail
- [ActivityLog] Step6: ETB Registration - Add Account to CIS Response1: Success (Log Level1) Response2: Fail (Log Level1)
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 15 years old, If no, return error If pass above dob validation then check - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’ and has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- OPO_03: Add Account to CIS OPO API detail - POST /opo/onboarding/customers/v1/etb/registration Request: products Response: Success/Failure
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- E1: Event topic: customer.created
- If Pass, OTP Verification
- If Pass, ID Card Expire
- If Pass, Mule Account
- If CIS = Success then start process in Camunda otherwise send failure message.
- E1: Event topic: customer.created
- If Pass, OTP Verification
- If Pass, ID Card Expire
- If Pass, Mule Account
- If CIS = Success then start process in Camunda otherwise send failure message.
- OPO_03: Add Account to CIS OPO API detail - /opo/registration/gateway/v1/task/products Request: products Response: Success/Failure
- E1: Event topic: customer.created - Customer profile (CIS No., External ID,…) Adobe will consume this topic in next phase.
- PFM1: Create PFM Profile Request: source.name, customer.name (CISID) Response: success, source.name, customer.name (CISID)
- If users already accepted PDPA clause 6, skip to Face verificatoin
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day

## Cleanup Contract

- Delete duplicate mobile no.
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- Terminate Stale Processes
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- Delete duplicate mobile no.
- Delete duplicate Email
- Terminate Stale Processes
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: email.delete
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- Delete duplicate mobile no.
- Delete duplicate Email
- Terminate Stale Processes
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: email.delete
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- Terminate Stale Processes
- Delete duplicate mobile no.
- If Pass, ID Card Expire
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Terminate Stale Processes
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Terminate Stale Processes
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check Card Expire, ID card photo.
- Terminate Stale Processes
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- Terminate Stale Processes
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- Delete duplicate mobile no.
- Terminate Stale Processes
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- Terminate Stale Processes
- If Pass, ID Card Expire
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- If Pass, ID Card Expire
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Terminate Stale Processes
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems

## Canonical Components Used

- [AuditLog] - actSubType = 'RM Add Relationship'
- [AuditLog] - actSubType = 'RM Update IAL'
- [AuditLog] in case Fail Only Inquiry Wrapper – Token
- [AuditLog] Inquiry wrapper – No token
- AF1: Set ECID to customerid for AppFlyer
- AF2: AppFlyer initialization
- Apigee (engagement)
- Apigee (Enterprise)
- Apigee (experience)
- AppsFlyer
- CDP
- CDP2: Update Identity
- CDP3: Update onboard success
- CH24
- CIAM
- CIAM binds the DPoP public key to the access token
- CIFS (CH24)
- CIS
- CIS ID, Authlevel = 3, successUrl = ‘EXIT_ETB’
- Consent Blob CMS
- Consent DB CMS
- Consent service CMS
- Darwinium
- Defer to MMP: Common service design/development
- DOPA Gateway
- ESIS
- FARA
- Fetch Task
- Firebase
- IAM Proxy
- JWT Token
- Kafka
- NA App
- NCBD Systems
- NCBD systems
- OPO (Camunda)
- OPO API detail - TBC
- OPO cache
- OPO-MS (Engagement)
- OPO-MS (engagement)
- OPO-MS (Experience)
- OPO-MS (experience)
- PDPA
- PFM
- Private API - Group System token issued by Ping
- Publish Event Topic: XXXX Event Type: XXXX
- REMOVE
- RM
- Send DWR Profile and Access token in background
- SMCS
- SMS Gateway
- Store DigitalID & DeviceBindingKey
- TBC
- TSP
