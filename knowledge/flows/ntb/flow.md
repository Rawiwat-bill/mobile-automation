# NTB Flow Knowledge

This file is generated from the canonical Visio source. Do not edit manually.

- Source Visio: `docs/source/sequence-diagrams/ntb/current/NTB_SequenceDiagram.vsdx`
- Synchronization date: `2026-08-06`
- Generation timestamp: `2026-08-06T04:16:16Z`

## Business Purpose

Canonical NTB business sequence represented by the Visio pages: NTB_Registration (MMP Lot#1); RTA_BeMyID; RTA_NDID; NTB_Registration (MMP Lot#2); NTB_Registration (Post-MMP1); Host_MMP Lot#2; RTA_BeMyID (MMP Lot#2); RTA_NDID (Lot#2); State_Handling(MMP); State_Handling(Post-MMP); [BK] NTB_Registration (MMP Lot#2); Host; Backup; NTB_Registration (MMP Backup)

## Expected Sequence

### Page 1: NTB_Registration (MMP Lot#1)

1. Related Hosts 1. RM 2.SmartCard 3. DOPA-Gateway 4. CH24 5. SMS Gateway 6. PWS 7. BLDG-NDID 8. FARA 9. SAS 10. ST 11. DGEN
2. Sequence Diagram - NTB Registration
3. 1 First Page (No Digital ID)
4. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
5. 2. Welcome Page
6. TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
7. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
8. Ask Permission for - Activity tracking - Push notification
9. Cache allowPushFlag
10. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
11. Submit device meta data Request: metadata, location, message Response: T&C URL
12. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, TandCUrl
13. 3. Accept T&C
14. System Token issued by PING
15. Auth_ID token (10minutes expired)
16. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
17. Auth ID token – return in every call, change to the new one every call (60 minutes expired)
18. Auth ID token in the request
19. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
20. 4. Input CitizenID, DoB & Mobile
21. Check sum and format of Citizen ID
22. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
23. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
24. Private API - Group System token issued by Ping
25. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
26. StartProcessByCID Request: citizen ID, DOB, idType Response: citizen ID, DOB, prompt laserCode
27. If CIS profile not found or CIS status is invalid, search RM
28. CIAM logic to separate flows Has CIS -> Reactivate No CIS, Has RM -> ETB No CIS, No RM -> NTB
29. [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
30. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPAFULL}/asset-type/{assetType=JSON} Response: blobData, mimeType, version
31. 5. Accept PDPA Consent
32. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
33. Save Customer PDPA Acceptance (AcceptanceFlag, ConsentDate, ConsentTypeValue)
34. 6. NTB Step
35. FARA (OCR Server)
36. Resolution 800 pixels
37. 7. Scan ID Card
38. Submit OCR Request: image base 64 binary Response: English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date *Remark Return value for Thai Title, English Title, Thai First Name, Thai Last Name, ID Number only
39. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
40. IAM_22 (new): Submit data to OCR Request: image base 64 binary Response: Detection Score, ID Number, Thai Birth Date, Thai Title, Thai First Name, Thai Last Name, expiryDate, issuerDate, gender, EN Title, EN First Name, EN Last Name, DOB
41. [CIAM Validate] 1. Detection Score >= 0.8 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
42. Prefill data from OCR 1. TitleNameTH / TitleNameEN 2. TH First name 3. TH Last name 4. CID (not editable)
43. ValidateLaserCode Request: idNum, LaserCodePID, Name, SurName, DOB, Response: prompt mobile number
44. IAM_05: Check DOPA (5 Fields) Request: PID, Name, SurName, DOB, LaserCode Response: ClientTransRef, ResponseCode, ResponseMesg
45. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
46. Validate 1. ID Expiry date >= Today 2. ID Issue Date <= Today
47. 8. Verify ID Card
48. Title name List hard code at frontend
49. [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
50. [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
51. IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
52. Save DOPADateTime
53. [CIAM Validate] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B", the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B", the customer will be treated as non-suspicious.
54. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
55. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
56. Validate 1. Mobile No. start with 06, 07, 08, 09 2. Mobile No. must have number 10 digits
57. SendSMSOTP Request: mobileNumber (in IA cache) Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
58. IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
59. 9. Verify Mobile No. By OTP
60. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: prompt PIN
61. [CIAM Validate] If OTP matches, then can proceed futher
62. IAM_23 (new): Create OPO profile Request: idNum, idType, Title Name Thai, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, ID Expiry Date, ID Issue Date, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion,TnCHash, PDPAFlag, PDPAPurposrCode, PDPAConsentDateTime, MobileNumber, DOPADateTime Response: ProcessInstantKey
63. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, ProcessInstantKey
64. #Cache PII data from CIAM
65. 10.1 Setup PIN
66. 10.2 Confirm PIN
67. Start Flow: Create Customer Temp Profile
68. Validate 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
69. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
70. If OPO returns error, end the flow.
71. Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
72. Validate 1. PIN and Confirm PIN is match
73. Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
74. Access Token AuthLevel = 3 CISId = Null ProcessInstantKey idenityStatus = preRegistration
75. Store Digital ID & DeviceBindingKey
76. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
77. Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
78. 11A.2 RTA-BeMyId Status Detail
79. 11A.1 Display Reference Code
80. 11. Select Authentication option
81. ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
82. ‘Processing’, ‘Register’ RTAStatus = ‘Processing’ or ‘Register’
83. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
84. ‘Locked’ RTAStatus = ‘Locked’
85. 11N.2
86. 11N.1
87. Get Latest RTA Record by CI and ProcessInstantKey
88. Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’ and ExpiryDateTime > DateTime.Now] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
89. If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
90. Please Continue sheet ‘RTA_BeMyID’ at Step then Back to Next step Mapping FlowType
91. OPO call delete Digital ID in user device and Direct customer to Beginning point
92. Logo Image should be get from Sitecore
93. If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
94. Image should be get from Sitecore
95. Please Continue sheet ‘RTA_NDID’ at Step then Back to Next step Mapping FlowType
96. In case have no RTA Record match by CI and ProcessInstantKey Then Get All RTA List from OPO DB by CI
97. Example IDP Error code with Warning Message
98. Screen Display depends on FlowType Validation
99. Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
100. 11B.4 RTA-NDID Status Detail
101. 11B.3 Pending Authen
102. ‘Error’ (RTAStatus = ‘ERROR’)
103. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
104. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
105. ‘Processing’ RTAStatus = ‘Processing’
106. Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
107. Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
108. OPO call delete Digital ID in user device and Direct customer to Beginning point
109. User Action : Select Authentication Option from [10D.1], [10D.2]
110. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
111. Please Refer to sheet ‘RTA_NDID’ or ‘RTA_BeMyID’ depends on customer selection
112. #Save State 2 - DigitalID - AuthLevel = -1 - ProcessInstantKey - State = 2
113. Validate All Lookup data has values Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
114. Get KYC Lookup Data (Fetch Task with Data return) Request: ProcessInstantKey Response: Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
115. Customer Tap ‘Next’
116. Common Service : Lookup Data
117. Get Customer Profile from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: idNum, Thai Title Name, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, Nationality, CountryOfResidence, PlaceOfBirth, MobileNumber,ContactNumber, OfficePhoneNumber, IDAddress, MaillingAddress, OfficeAddress, Education, Occupation, TypeOfBusiness, Position, OfficeName, SourceOfAsset, SourceOfFund, IncomePermonth, AssetValue, EarningCountry1-3 Remark: To get previous input in Customer KYC Section
118. 12. Input KYC Information
119. 12.1 Personal Detail
120. 12.2 Contact Information
121. 12.3 Education & Employment
122. 12.4 Income & Assets
123. 12.5 KYC Summary
124. If Customer Search Address
125. Common Service : Lookup Address
126. If Customer Search Country for Earning Country
127. Common Service : Lookup Country
128. Save information from Customer input to OPO DB (Temp)
129. Save KYC Information (Fetch Task) Request: ProcessInstantKey, KYC Information (each page) Response:
130. If Customer Tap ‘Next’ at Each page
131. If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
132. If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
133. If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
134. Start Flow : Header: X-Language, X-Channel, Access Token Response: Selfie Face callback
135. Check Profile at Ping - No CIS ID - Validate Auth level = 3 - idenityStatus = preRegistration
136. Get CustomerProfile Temp from OPO (Instead of CIS) Request:ProcessInstantKey Response:ID, IDType, IDExpiryDate, Nationality(For Foriegner in the future), AuthenticationMethod, ReferenceId
137. IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
138. Face Comparison Request: selfieImage Response: Status
139. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
140. 13.1 Intro before Face Scan
141. Get IDPImage-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, ImageBase64
142. If AuthenticationMode = ‘NDID’
143. Ask for camera permission
144. Liveness checking Capture selfie image
145. 13.2 Take a Selfie Photo for Face Scan
146. N E C
147. IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
148. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
149. CIAM checks bblscore. If it equals to 3, then can proceed further
150. 13.3 Face Scan Processing
151. If fail
152. If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
153. Onboard Customer Request: ProcessInstantKey, requestId Response: CISID Remark:
154. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
155. If pass face compare
156. Get Customer Profile Temp from OPO DB Objective: To Get CitizenId for CustomerSearch and Customer Profile Info for Create Profile
157. IAM_25 (new): Onboard Customer Header: ProcessInstantKey Request: requestId Response: cisId
158. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
159. Customer Search by Citizen ID Request: idNum Response: RMNo, CitizenId, RMNo
160. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: RMNo, CitizenId, DoB
161. Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
162. CIS_Wrapper (2) : Get Customer Profile by RM No POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: RMNO, {customerProfile, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, customerProfileEdd} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
163. If RMNo. Has value
164. Get Customer Profile by RMNo Request: RMNo. Response: All response fields from CIS
165. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
166. Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
167. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
168. Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
169. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
170. Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
171. Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
172. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
173. If: No RM Profile (Create CISID, Create RMNO)
174. - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
175. Validate Response No CIS, No RM -> Call Next Process H14:Create Customer Profile at RM No CIS, Has RM -> Call Next Process H15:Update Customer KYC at RM
176. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
177. If: Has RM Profile (Create CISID, Update RM Profile)
178. - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
179. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
180. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
181. Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
182. Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
183. Access Token AuthLevel = 3 CIS ID ProcessInstantKey = Null idenityStatus = active
184. Update DigitalID Profile with 1. CIS ID 2. ProcessInstantKey= Null
185. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
186. E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
187. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
188. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
189. If API update CustomerProfileRelAdd fail
190. E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
191. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
192. Check if duplicate mobile no. in CIS Profile
193. If found duplicate mobile no.
194. Delete duplicate mobile no.
195. E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
196. [QA] CIS will update to KAFKA then IAM subscribe for recheck flag hasMobile No.
197. E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
198. H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
199. EOD Process (Existing) File - Batch Update RM profile (RM no., Phone number) File - Batch update relationship (RM No., CIS No.)
200. TSP
201. Apigee (engagement)
202. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
203. OPO get EntraID (Virtual ID)
204. Retry 3 times
205. #Save State 3 - DigitalID - AuthLevel = 3 - State = 3
206. 14. Intro page to start apply product
207. Get Product Eligible [NEW] Request: CISID Response: ProductList {ProductId, ProductType, ProductNamtTH, ProductNameEN}
208. CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
209. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
210. Get Product Eligible Request: IDType, CTCode, DOB, BBLIAL, IDPIAL, RiskLevel Response: ProductList{ProductId, ProductType, ProductNamtTH, ProductNameEN}
211. CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
212. 15. Eligible Product list
213. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
214. Please Refer to Open eSaving Sequence Diagram at Step ‘Get Product Detail’
215. Note Mapping Request Type for Face Compare
216. 11B.4 NDID RTA status ‘Approved’
217. 11A.2 BeMyID RTA status ‘Verified’
218. CIS_Wrapper (3): Create Customer Profile-NTB POST: /customerprofile/api/v2/cis/internal/customers/new Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileIdentifications, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, contactNumber, email, agreement, consent, pdpa, channel, classification} Action: "CREATE_CUSTOMER_PROFILE" Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
219. CIS_Wrapper(3): Create Customer Profile-NTB (No CISID, has RMNO) Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, profile, contactNumber, agreement, identity, identifier, channel, classification, pdpa, consent, email} Action: CREATE_CUSTOMER_NTB_WITH_RM Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
220. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
221. Logo IDP Bank App *Not Existing* Need to Place Image on Sitecore for New category and has configuration to get these logoes
222. Display Refence Code with ReferenceId last 7 digits in UpperCase format
223. B_CheckRTA #SubFlow
224. B_CheckRTA
225. M_CheckRTA
226. Set Save State = 1, Expiry date = 7 days
227. N_CheckRTA #SubFlow
228. B_Re-Gen RefNo
229. M_Re-Gen RTA
230. B_Cancel RTA
231. M_Cancel RTA
232. CIS_11: Get Customer Profile Request: CIS ID Response: cisId, partyCertificateType (idType), identifierType (RMNO, EXTID), identifierTypeValue, partyPrefix, partyFirstName, partyLastname, partyPrefixEn, partyFirstNameEn, partyLastNameEN, partyFullNameEn, partydisplayName, dob, partyBlockedStatus, classificationType, classificationTypevalue, partyChannelStatus, partyChannelBlock
233. Liveness Check If Yes, do face compare
234. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version

### Page 2: RTA_BeMyID

1. #Save State 1 - DigitalID - AuthLevel = -1 - ProcessInsantKey - State = 1
2. 10. Select Authentication option
3. Get Customer Profile from cache
4. Get Latest RTA Record by CI and ProcessInstantKey
5. Genereate RTA-BeMyId Request: ProcessInstantKey Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, MachineName, RTAApprovedDateTime, ServicePointUrl
6. Validate RTA Record If [RTAStatus = ‘Register’ or ‘Processing’] then,Return General Error Else, proceed next step to call Generate CustomerRefNo
7. Generate CustomerRefNo 7 digits - Bank Code (2 digits) : Fixed value ‘02’ - Partner Code (2 digits) : Fixed value ‘04’ - Running number (3 digits)
8. Insert New Running RefCode Per CI
9. Generate ReferenceId format: B_Channel_YYYYMMDD_GUID
10. H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType (‘TC01’), durationOfTimeout(48hr from config), partnerId (‘04’) Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
11. Validate Response If (H6) HTTP response code = 200 and responseCode = 000 Then, Insert DB with ReferenceId, IdNum, ProcessInstantKey, RTAId, RTACreateDateTime, RTAStatus = (status), RTAExpiryDateTime = (RTACreateDateTime+Duration Of Timeout)
12. 10A.1 Display Reference Code
13. Cancel RTA-BeMyId Request: ProcessInstantKey, ReferenceId Response: FlowType
14. Customer Action :
15. If Customer Action: Tap ‘Change Method’
16. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey *Remark: To get CustomerRefNo
17. Proceed count down time Calculated from ExpiryDateTime – DateTime.Now
18. Validate RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to next step H6: GenerateRTA-BeMyID Else if RTAStatus = ‘Locked’ or ‘Expired’ or ‘Rejected’ Then Skip H6 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
19. Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
20. Update DB with UpdateDateTime, RTA Status = ‘Cancelled’
21. H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
22. 10. Select Authentication option
23. 10N.2
24. 10N.1
25. Get All RTA List from OPO DB by CI
26. Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
27. Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
28. Get RTA Status-BeMyId Request: ProcessInstantKey, ReferenceId, Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, RefCode, MachineName, RTAApprovedDateTime, ServicePointUrl
29. If Customer Action: Tap ‘I’ve Enter My code’
30. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey
31. 10A.1 Display reference code
32. 10A.2 RTA-BeMyId Status Detail
33. H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
34. ‘Verified’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘N’)
35. ‘Processing’ RTAStatus = ‘Processing’
36. ‘Register’ RTASTatus = ‘Register’
37. ‘Expired’ RTAStatus = ‘Expired’
38. ‘Rejected’ RTAStatus = ‘Rejected’
39. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
40. ‘Locked’ RTAStatus = ‘Locked’
41. Validate RTAStatus If RTAStatus = ‘Register’ and ExpiryDateTime > DateTime.Now or RTAStatus = ‘Processing’ then, proceed next step to call (H7): InquiryRTA-BeMyID
42. 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
43. RTA Status: ‘Verified’
44. Get Customer Profile from OPO DB
45. User Press ‘OK’, pop-up will be closed and still being in [10A.1] Display Reference Code
46. OPO call delete Digital ID in user device and Direct customer to Beginning point
47. Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H7 as below: If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If ID Number is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If Issue Date is match then Set IssueDate_PassValidateFlag = ‘Y’ Else IssueDate_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
48. CTA Scenario
49. Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
50. After customer Tap at this CTA, Continue service at Tap ‘NTB_Registration’
51. Mapping Response ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, MachineName, RTAApprovedDateTime, ServicePointUrl (from Configuration)
52. Please Refer to sheet ‘NTB Registration’ to continue Save State 2 Process
53. B_CheckRTA #SubFlow
54. New Entry

### Page 3: RTA_NDID

1. #Save State 1 - DigitalID - AuthLevel = -1 - ProcessInsantKey - State = 1
2. 10. Select Authentication option
3. Get NDID T&C Content Request: language, type =”NDID_TC” Response: version, ndidcontentUrl
4. Consent service CMS
5. Consent DB CMS
6. Consent Blob CMS
7. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NDID}/doc-type/{docTypeCode4=NTNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
8. Update NDID T&C Acceptance (Fetch Task) Request: ProcessInstantKey, ndidConsentVersion, ndidConsentDateTime, ndidConsentFlag Response:
9. 10B.1 Accept NDID T&C
10. Update NDID T&C Acceptance
11. Example: IDP Whitelist Configuration [ { "company_code": "002", "industryCode": "001", "app_name_thai": "บัวหลวง เอ็มแบงก์กิ้ง", "app_name_eng": "Bualuang mBanking" }, { "company_code": "004", "industryCode": "001", "app_name_thai": "K Plus", "app_name_eng": "K Plus" } ]
12. H8: Get IDP List [New Service] URL: POST /NDIDSwagger/RPServices/utility/idp_list Request: NameSpace = ‘citizen_id’, Citizen ID, Min IAL=2.3, Min AAL=2.2 Response: Node ID, Max IAL, Max AAL, Preferred IDP Flag, Industry Code Company Code, Thai Marketing Name, English Marketing Name, Thai Proxy or Subsidiary Name,English Proxy or Subsidiary Name, Role, Running
13. Get IDP List (Fetch Task with Data return) Request: ProcessInstantKey Response: IDPList {NodeID, PreferredIDPFlag, IndustryCode, CompanyCode, appNameTh, appNameEn, Role, Running, IDPBankLogoUrl}
14. Validate IDP List If IDP has Preferred IDP Flag = ‘Y’ Then display IDP in section ‘Enrolled’ Elese, display in Section ‘Not Enrolled’
15. 1. Filter IDP Only Return from Role=”IDP” 2. Check IDP Whitelist Configuration Return only IDP List that match in IDP whitelist configuration and sort by company_code asending 3. Mapping Additional Response ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode
16. Genereate RTA-NDID (Fetch Task with Data return) Request: idp_id_list Response: ReferenceId, RTAStatus, RTACreateDateTime, RTAExpiryDateTime, appNameTh, appNameEn , IDPBankLogoUrl
17. 10B.2 Select Provider
18. “ขอยืนยันตัวตนเพื่อใช้บริการกับธนาคารกรุงเทพ และประสงค์ให้ส่งข้อมูลประกอบการยืนยันตัวตนพร้อมรูปถ่ายให้ธนาคาร” concat with string “(รหัสอ้างอิง: { Last 8 digits of ReferenceId with Upper case })” Example: ขอยืนยันตัวตนเพื่อใช้บริการกับธนาคารกรุงเทพ และประสงค์ให้ส่งข้อมูลประกอบการยืนยันตัวตนพร้อมรูปถ่ายให้ธนาคาร รหัสอ้างอิง: RE7H05TS
19. 1. Get RTA List from OPO DB by CI If Count of ReferendId start with ‘NCBD_XXX’ >= 10 then, return Error Else continue Next to Get Latest RTA 2. Get Latest RTA Record by CI and ProcessInstantKey If RTAStatus = ‘Processing’ Then, Return General Error Else, proceed next step to call Generate ReferenceId
20. Fields in orange highlight should be in configuration
21. H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
22. Generate ReferenceId format: NCBD_YYYYMMDD_GUID
23. Navigate to 10. Select Authentication option
24. Validate Response If (H9) HTTP response code = 202 and RequestId has value Then, Insert DB with ReferenceId, RequestId, IDNum, ProcessInstantKey, UpdateDateTime, RTAStatus = ‘Processing’, RTACreateDateTime, CompanyCode, IndustryCode, appNameTh, appNameEn
25. Mapping Response ReferenceId, RTAStatus = ‘Processing’, RTACreateDateTime (default to RequestDatetime), RTAExpiryDateTime (default to RequestDatetime + request_timeout), IDPBankLogoUrl(PrefixURL + CompanyCode), appNameTh = app_name_thai, appNameEn = app_name_eng
26. Customer Action :
27. Cancel RTA-NDID Request: ProcessInstantKey, ReferenceId, Response: FlowType
28. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey
29. If Customer Action: Tap ‘Change Method’
30. 10B.3 Pending Authen
31. Proceed count down time Calculated from ExpiryDateTime – DateTime.Now
32. H11: Close RTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
33. Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
34. Display Refence Code with ReferenceId last 7 digits in UpperCase format
35. Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
36. Validate Response If (H9) HTTP response code = 202 Update DB with UpdateDateTime, RTAStatus = ‘Cancelled’
37. 10. Select Authentication option
38. 10N.2
39. 10N.1
40. Get All RTA List from OPO DB by CI
41. Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
42. Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
43. If Customer Action: Tap ‘I’ve already authenticated’
44. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey
45. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
46. Get RTA Status-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl
47. Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed next step to call (H10): Get RTA Status-NDID
48. Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
49. Validate RTA Expiry If Not Expired then, Proceed further Else, Update DB with UpdateDateTime, RTAStatus = ‘Expired’
50. 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
51. Get OPO User Temp Profile
52. If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
53. Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H10 as below: #To Be Revise If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If English First Name is match then Set FirstNameEN_PassValidateFlag = ‘Y’ Else FirstNameEN_PassValidateFlag = ‘N’ If English Last Name is match then Set LastNameEN_PassValidateFlag = ‘Y’ Else LastNameEN_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If ID is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
54. 10B.3 Pending Authen
55. 10B.4 RTA-NDID Status Detail
56. ‘Processing’ RTAStatus = ‘Processing’
57. ‘Expired’ RTAStatus = ‘Expired’
58. ‘Rejected’ RTAStatus = ‘Rejected’
59. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
60. ‘Error’ (RTAStatus = ‘Error’)
61. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
62. Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
63. Mapping Response ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, RTAApprovedDateTime, appNameTh, appNameEn, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl = ‘PrefixURL’ (from config) + CompanyCode
64. OPO call delete Digital ID in user device and Direct customer to Beginning point
65. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
66. Please Refer to sheet ‘NTB Registration’ to continue #Save State 2 Process
67. New Entry
68. N_CheckRTA #SubFlow

### Page 4: NTB_Registration (MMP Lot#2)

1. Sequence Diagram - NTB Registration
2. 0. Splash screen
3. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
4. 1. Welcome & Orientation
5. 1. First Page
6. Ask permission for Push Notification & Activity tracking
7. Start Customer Enrollment Journey Header: X-Language, X-Channel Response: nonce with key/app attestation
8. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
9. Generate nonce
10. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 1 - Responds back with a callback to collect key/app attestation - End flow - Customized error - End flow - OOTB error
11. Submit attestation data Header: X-DPoP-Token, X-DBA-Token Request: key attestation, app attestation Response: device profile collector callback
12. Trust Assurance Service
13. [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
14. CIAM validates DPoP proof
15. IAM_40: App and Key Attestation Verification Request: platform, nonce, keyMaterial, attestationBundle Response: keyAttestation { trusted, keyStoreType, publicKey }, appAttestation { trusted, riskScore, decision }
16. Remark: Every request to CIAM requires X-DPoP-Token and CIAM needs to validate the DPoP proof
17. [AuditLog] IAM Proxy sheet - IAM_40 Response
18. CIAM validates key and app attestation results returned from TAS
19. Submit device meta data Request: metadata, location, message Response: T&C URL
20. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 2 - Responds back with a DeviceProfileCallback - Response 2.1 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - Response 2.2 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - End flow - Customized error - End flow - OOTB error
21. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
22. IAM_01: T&C content Inquiry Header: accept-language Response: version, hash, tandCpage
23. Back to First Landing
24. System Token issued by PING
25. 3. Accept T&C
26. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 3 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
27. [AuditLog] IAM Proxy sheet - IAM_01 Response
28. Auth_ID token (10minutes expired)
29. Auth ID token – return in every call, change to the new one every call (60 minutes expired)
30. Auth ID token in the request
31. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
32. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
33. 4. Input CitizenID, DoB & Mobile
34. Check sum and format of Citizen ID
35. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
36. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
37. Private API - Group System token issued by Ping
38. IAM_02: Customer Search Request: idNum, idType {customerSearch} Response: cisId, cisExternalId, cisIdStatus, channels [], rmNum, dob, isDemoUser, mobileNumber
39. StartProcessByCID Request: citizen ID, DOB, idType Response: citizen ID, DOB, prompt laserCode
40. If CIS profile not found or CIS status is invalid, search RM
41. CIAM logic to separate flows Has CIS -> Reactivate No CIS, Has RM -> ETB No CIS, No RM -> NTB
42. [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
43. [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
44. [AuditLog] IAM Proxy sheet - IAM_02 Response
45. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - go back to T&C - End flow - Customized error - End flow - OOTB error
46. 5. Accept PDPA Consent
47. IAM_10: Get PDPA content Header: accept-language Request: onboardingFlowType Response: version, pdpaContent, hash
48. [ActivityLog] Step 4 - NTB - Citizen ID and DOB Continued - Response 4.1 - Response with PDPA - End flow - Customized error - End flow - OOTB error
49. [AuditLog] IAM Proxy sheet - IAM_10 Response
50. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPAFULL}/asset-type/{assetType=JSON} Response: blobData, mimeType, version
51. Save Customer PDPA Acceptance (AcceptanceFlag, ConsentDate, ConsentTypeValue)
52. 6. NTB Step
53. [ActivityLog] Step 5 - NTB Onboarding - Full PDPA Consent - Response 5.1 - Response with OCR - End flow - OOTB error
54. FARA (OCR Server)
55. Resolution 800 pixels
56. 7. Scan ID Card
57. Submit OCR Request: image base 64 binary Response: English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date *Remark Return value for Thai Title, English Title, Thai First Name, Thai Last Name, ID Number only
58. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
59. IAM_22: Submit data to OCR Request: image base 64 binary Response: Detection Score, ID Number, Thai Birth Date, Thai Title, Thai First Name, Thai Last Name, expiryDate, issuerDate, gender, EN Title, EN First Name, EN Last Name, DOB
60. [AuditLog] IAM Proxy sheet - IAM_22 Response
61. [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
62. [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 4, if not, returns in-flow error (users can retry)
63. Prefill data from OCR 1. TitleNameTH / TitleNameEN 2. TH First name 3. TH Last name 4. CID (not editable)
64. ValidateLaserCode Request: idNum, LaserCodePID, Name, SurName, DOB, Response: prompt mobile number
65. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg, Code, Desc
66. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
67. Validate 1. ID Expiry date >= Today 2. ID Issue Date <= Today
68. 8. Verify ID Card
69. Title name List hard code at frontend
70. [AuditLog] IAM Proxy sheet - IAM_05 Response
71. [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
72. [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
73. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
74. Save DOPADateTime
75. [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
76. [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
77. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
78. [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
79. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
80. Validate 1. Mobile No. start with 06, 07, 08, 09 2. Mobile No. must have number 10 digits
81. IAM_08: Send SMS OTP Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0 ...
82. SendSMSOTP Request: mobileNumber (in IA cache) Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
83. [AuditLog] IAM Proxy sheet - IAM_08 Response
84. 9. Verify Mobile No. By OTP
85. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: prompt PIN
86. [CIAM Validate] If OTP matches, then can proceed futher
87. [ActivityLog] Step 8 - NTB Onboarding - Verify Mobile using OTP - Response 8.1 - Response with PIN - Response - 8.2 - Resend OTP - In flow error Response 8.3.1 - OTP is incorrect (1 attempt) - In flow error Response 8.3.2 - OTP is incorrect (2 attempt) - In flow error Response 8.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
88. IAM_23: Create OPO profile Request: idNum, idType, Title Name Thai, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, ID Expiry Date, ID Issue Date, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion,TnCHash, PDPAFlag, PDPAPurposrCode, PDPAConsentDateTime, MobileNumber, DOPADateTime Response: ProcessInstantKey
89. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, ProcessInstantKey
90. #Cache PII data from CIAM
91. 10.1 Setup PIN
92. 10.2 Confirm PIN
93. Start Flow: Create Customer Temp Profile
94. Validate 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
95. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
96. If OPO returns error, end the flow.
97. Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
98. Validate 1. PIN and Confirm PIN is match
99. Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
100. Access Token AuthLevel = 3 CISId = Null ProcessInstantKey idenityStatus = preRegistration
101. Store Digital ID & DeviceBindingKey
102. [AuditLog] Step 9 - NTB Onboarding - Register PIN - Response 9 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
103. [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
104. [AuditLog] Step 10 - NTB Onboarding - Bind Device - Response 10 - end of the onboarding process save state 1 - End flow - Customized error - End flow - OOTB error
105. [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
106. [AuditLog] IAM Proxy sheet - IAM_23 Response
107. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
108. Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
109. 11A.2 RTA-BeMyId Status Detail
110. [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
111. 11A.1 Display Reference Code
112. 11. Select Authentication option
113. ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
114. ‘Processing’, ‘Register’ RTAStatus = ‘Processing’ or ‘Register’
115. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
116. ‘Locked’ RTAStatus = ‘Locked’
117. 11N.2
118. 11N.1
119. Get Latest RTA Record by CI and ProcessInstantKey
120. Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
121. If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
122. Please Continue sheet ‘RTA_BeMyID’ at Step then Back to Next step Mapping FlowType
123. OPO call delete Digital ID in user device and Direct customer to Beginning point
124. Logo Image should be get from Sitecore
125. If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
126. Image should be get from Sitecore
127. Please Continue sheet ‘RTA_NDID’ at Step then Back to Next step Mapping FlowType
128. In case have no RTA Record match by CI and ProcessInstantKey Then Get All RTA List from OPO DB by CI
129. Example IDP Error code with Warning Message
130. Screen Display depends on FlowType Validation
131. Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
132. 11B.4 RTA-NDID Status Detail
133. 11B.3 Pending Authen
134. ‘Error’ (RTAStatus = ‘ERROR’)
135. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
136. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
137. ‘Processing’ RTAStatus = ‘Processing’
138. Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
139. Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
140. OPO call delete Digital ID in user device and Direct customer to Beginning point
141. User Action : Select Authentication Option from [10D.1], [10D.2]
142. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
143. Please Refer to sheet ‘RTA_NDID’ or ‘RTA_BeMyID’ depends on customer selection
144. #Save State 2 - DigitalID - AuthLevel = 3 - ProcessInstantKey - State = 2
145. Validate All Lookup data has values Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
146. Get KYC Lookup Data (Fetch Task with Data return) Request: ProcessInstantKey Response: Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
147. Customer Tap ‘Next’
148. Common Service : Lookup Data
149. Get Customer Profile from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: idNum, Thai Title Name, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, Nationality, CountryOfResidence, PlaceOfBirth, MobileNumber,ContactNumber, OfficePhoneNumber, IDAddress, MaillingAddress, OfficeAddress, Education, Occupation, TypeOfBusiness, Position, OfficeName, SourceOfAsset, SourceOfFund, IncomePermonth, AssetValue, EarningCountry1-3 Remark: To get previous input in Customer KYC Section
150. 12. Input KYC Information
151. 12.1 Personal Detail
152. 12.2 Contact Information
153. 12.3 Education & Employment
154. 12.4 Income & Assets
155. 12.5 KYC Summary
156. [ActivityLog] Step 15 - NTB Registration – Get Customer Information Response2: Fail (Log Level1)
157. If Customer Search Address
158. Common Service : Lookup Address
159. If Customer Search Country for Earning Country
160. Common Service : Lookup Country
161. Save information from Customer input to OPO DB (Temp)
162. Save KYC Information (Fetch Task) Request: ProcessInstantKey, KYC Information (each page) Response:
163. If Customer Tap ‘Next’ at Each page
164. If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
165. [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
166. If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
167. [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
168. [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
169. [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
170. If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
171. [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
172. Start Flow : Header: X-Language, X-Channel, Access Token Response: Selfie Face callback
173. Check Profile at Ping - No CIS ID - Validate Auth level = 3 - idenityStatus = preRegistration
174. [ActivityLog] Step 1 - NTB Onboarding Face Verification – Initiate - Response 1 - Response with Facial Verification - End flow - Customized error - End flow - OOTB error
175. Get CustomerProfile Temp from OPO (Instead of CIS) Request:ProcessInstantKey Response:ID, IDType, IDExpiryDate, Nationality(For Foriegner in the future), AuthenticationMethod, ReferenceId
176. IAM_24: Get profile from OPO Request: requestId, processInstanceKey Response: status
177. Face Comparison Request: selfieImage Response: Status
178. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
179. 13.1 Intro before Face Scan
180. Get IDPImage-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, ImageBase64
181. If AuthenticationMode = ‘NDID’
182. Ask for camera permission
183. Liveness checking Capture selfie image
184. [AuditLog] IAM Proxy sheet - IAM_24 Response
185. 13.2 Take a Selfie Photo for Face Scan
186. N E C
187. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
188. IAM_20 Face Comparison Request: imageFile, requestId, requestChannel Response: status, Confidencescore, bblscore
189. CIAM checks bblscore. If it equals to 3, then can proceed further
190. 13.3 Face Scan Processing
191. If fail
192. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
193. If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
194. Onboard Customer Request: requestId, ProcessInstanceKey Response: cisId, cisExternalId
195. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
196. If pass face compare
197. Get Customer Profile Temp from OPO DB Objective: To Get CitizenId for CustomerSearch and Customer Profile Info for Create Profile
198. IAM_25: Onboard Customer Request: requestId, ProcessInstanceKey Response: cisId, cisExternalId
199. CIS_Wrapper(4) (new): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
200. CH24
201. Get Customer Profile by ID Number Request: idNum Response: All response fields from CIS
202. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
203. [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
204. [AuditLog] in case Fail/Success Only API Inquiry without JWT token
205. Validate Response If status.code is “2005”, refer case “RMNo Has no Value” Otherwise, refer case “RMNo Has Value”
206. Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
207. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
208. [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
209. Validate Response If RiskRating < 3, Then update Risk Level, Risk Reason Code into (Customer Profile Temp of OPO DB) proceed next step to Save State Expiry. Else, return error
210. Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
211. Set segmentLevel = A13 A05 for default segment of “Create Customer Profile-NTB”
212. Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
213. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
214. If: No RM Profile (Create CISID, Create RMNO)
215. - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
216. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
217. If identityVerifiedChannel = 002 beMyId
218. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
219. [AuditLog] in case Fail/Success Only CIS RM Update IAL
220. If: Has RM Profile (Create CISID, Update RM Profile)
221. - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
222. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
223. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
224. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
225. Check if duplicate mobile no. in CIS Profile
226. If found duplicate mobile no.
227. Delete duplicate mobile no.
228. [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
229. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
230. Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
231. [AuditLog] in case Fail/Success Only API CREATE ACTION:
232. Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
233. Access Token AuthLevel = 3 cisId cisExternalId ProcessInstanceKey = Null idenityStatus = active
234. Update DigitalID Profile with 1. cisId 2. ProcessInstanceKey= Null 3. cisExternalId
235. [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
236. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - Response 2 - end of the onboarding process save state 3 - Response 2 - end of the onboarding process save state 3 (collect Device Info) IAM Proxy sheet - IAM_25 Response
237. [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
238. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
239. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
240. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
241. [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
242. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
243. [AuditLog] in case Fail/Success Only Backend API Update PDPA
244. If API update Host or Kafka fail, re execute fail process (retry X times)
245. Write fail payload to DB
246. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result
247. [AuditLog] - actSubType = 'RM Add Relationship'
248. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
249. [AuditLog] - actSubType = 'RM Update IAL'
250. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
251. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
252. EOD Process (Existing) File - Batch Update RM profile (RM no., Phone number) File - Batch update relationship (RM No., CIS No.)
253. Prepare data for Call “H21: Get Daily Total Limit”. Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 4. RM Number Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now 2. RM Number from Response of “Create Customer Profile-NTB”
254. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
255. oCRM
256. If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
257. CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
258. Update Segment Level Request: CIS ID, Segment Response: All response fields from CIS
259. [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
260. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. settingsDetails/transactionLimitScheme​ = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”“05”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
261. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
262. TSP
263. If Update Segment Level failed,
264. OPO get EntraID (Virtual ID)
265. [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
266. Retry 3 times
267. AppsFlyer
268. Adobe SDK
269. Firebase
270. [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
271. [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
272. Remark: This is an independent process
273. Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
274. CNH
275. Always Get Pushed Token from FCM by not consider on PushNotification OS
276. If Fail, then make pendingRegisterFlag is true
277. #Save State 3 - DigitalID - AuthLevel = 3 - State = 3
278. 14. Intro page to start apply product
279. Get Product Eligible [NEW] Request: CISID Response: ProductList {ProductId, ProductType, ProductNamtTH, ProductNameEN}
280. CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
281. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
282. [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
283. Get Product Eligible Request: IDType, CTCode, DOB, BBLIAL, IDPIAL, RiskLevel Response: ProductList{ProductId, ProductType, ProductNamtTH, ProductNameEN}
284. CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {customerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
285. 15. Eligible Product list
286. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
287. [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
288. Please Refer to Open eSaving Sequence Diagram at Step ‘Get Product Detail’
289. Note Mapping Request Type for Face Compare
290. 11B.4 NDID RTA status ‘Approved’
291. 11A.2 BeMyID RTA status ‘Verified’
292. CIS_Wrapper (13): Create Customer Profile-NTB POST: /customerprofile/api/v2/cis/internal/customers/new Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileIdentifications, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, contactNumber, email, agreement, consent, pdpa, channel, classification, channelProfile} Action: "CREATE_CUSTOMER_PROFILE" Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
293. CIS_Wrapper(14): Create Customer Profile-NTB (No CISID, has RMNO) Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, profile, contactNumber, agreement, identity, identifier, channel, classification, pdpa, consent, email} Action: CREATE_CUSTOMER_NTB_WITH_RM Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
294. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
295. Logo IDP Bank App *Not Existing* Need to Place Image on Sitecore for New category and has configuration to get these logoes
296. Display Refence Code with ReferenceId last 7 digits in UpperCase format
297. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
298. B_CheckRTA #SubFlow
299. B_CheckRTA
300. M_CheckRTA
301. Set Save State = 1, Expiry date = 7 days
302. Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
303. N_CheckRTA #SubFlow
304. B_Re-Gen RefNo
305. M_Re-Gen RTA
306. B_Cancel RTA
307. M_Cancel RTA
308. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
309. CDP2: Update Identity
310. CDP3: Update Onboard success
311. Liveness Check If Yes, do face compare
312. AF1: Set ECID to customerid for AppsFlyer
313. A21: AppsFlyer initialization
314. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
315. CIAM binds the DPoP public key to the access token
316. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
317. Non sequential step

### Page 5: NTB_Registration (Post-MMP1)

1. Sequence Diagram - NTB Registration
2. 0. Splash screen
3. POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3 - Add DWR Device profiling at beginning of onboarding and before request EFM to approval Remark: Since DWN charging model so decided to add at Entry - Add API call to EFM for request to approve - [#TBC] EFM Advice message via KAFKA
4. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
5. 1. Welcome & Orientation
6. 1. First Page
7. Ask permission for Push Notification & Activity tracking
8. Start Customer Enrollment Journey Header: X-Language, X-Channel Response: nonce with key/app attestation
9. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
10. Generate nonce
11. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 1 - Responds back with a callback to collect key/app attestation and app/os version - End flow - Customized error - End flow - OOTB error
12. Submit attestation data Header: X-DPoP-Token, X-DBA-Token Request: key attestation, app attestation Response: device profile collector callback
13. Trust Assurance Service
14. [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
15. CIAM validates DPoP proof
16. IAM_40: App and Key Attestation Verification Request: platform, nonce, keyMaterial, attestationBundle Response: keyAttestation { trusted, keyStoreType, publicKey }, appAttestation { trusted, riskScore, decision }
17. Remark: Every request to CIAM requires X-DPoP-Token and CIAM needs to validate the DPoP proof
18. [AuditLog] IAM Proxy sheet - IAM_40 Response
19. CIAM validates key and app attestation results returned from TAS
20. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 2 - Responds back with a DeviceProfileCallback - Response 2.1 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - Response 2.2 - Responds back with a DeviceProfileCallback with an inflow error for App upgrade - End flow - Customized error - End flow - OOTB error
21. TBC
22. Darwinium
23. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
24. Submit device meta data Request: metadata, location, message Response: T&C URL
25. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
26. Back to First Landing
27. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 3 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
28. IAM_01: T&C content Inquiry Header: accept-language Response: version, hash, tandCpage
29. 3. Accept T&C
30. System Token issued by PING
31. Auth_ID token (10minutes expired)
32. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
33. Auth ID token – return in every call, change to the new one every call (60 minutes expired)
34. [AuditLog] IAM Proxy sheet - IAM_01 Response
35. Auth ID token in the request
36. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
37. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
38. 4. Input CitizenID, DoB & Mobile
39. Check sum and format of Citizen ID
40. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
41. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
42. Private API - Group System token issued by Ping
43. IAM_02: Customer Search Request: idNum, idType {customerSearch} Response: cisId, cisExternalId, cisIdStatus, channels [], rmNum, dob, isDemoUser, mobileNumber
44. StartProcessByCID Request: citizen ID, DOB, idType Response: citizen ID, DOB, prompt laserCode
45. If CIS profile not found or CIS status is invalid, search RM
46. CIAM logic to separate flows Has CIS -> Reactivate No CIS, Has RM -> ETB No CIS, No RM -> NTB
47. [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
48. [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
49. [AuditLog] IAM Proxy sheet - IAM_02 Response
50. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - go back to T&C - End flow - Customized error - End flow - OOTB error
51. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NTB :transaction success | IA Cust Error Code: transaction fail Response:
52. 5. Accept PDPA Consent
53. IAM_10: Get PDPA content Header: accept-language Request: onboardingFlowType Response: version, pdpaContent, hash
54. [ActivityLog] Step 4 - NTB - Citizen ID and DOB Continued - Response 4.1 - Response with PDPA - End flow - Customized error - End flow - OOTB error
55. [AuditLog] IAM Proxy sheet - IAM_10 Response
56. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPAFULL}/asset-type/{assetType=JSON} Response: blobData, mimeType, version
57. Save Customer PDPA Acceptance (AcceptanceFlag, ConsentDate, ConsentTypeValue)
58. 6. NTB Step
59. [ActivityLog] Step 5 - NTB Onboarding - Full PDPA Consent - Response 5.1 - Response with OCR - End flow - OOTB error
60. FARA (OCR Server)
61. Resolution 800 pixels
62. 7. Scan ID Card
63. Submit OCR Request: image base 64 binary Response: English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date *Remark Return value for Thai Title, English Title, Thai First Name, Thai Last Name, ID Number only
64. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
65. IAM_22: Submit data to OCR Request: image base 64 binary Response: Detection Score, ID Number, Thai Birth Date, Thai Title, Thai First Name, Thai Last Name, expiryDate, issuerDate, gender, EN Title, EN First Name, EN Last Name, DOB
66. [AuditLog] IAM Proxy sheet - IAM_22 Response
67. [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
68. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘IDCard’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
69. [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 4, if not, returns in-flow error (users can retry)
70. Prefill data from OCR 1. TitleNameTH / TitleNameEN 2. TH First name 3. TH Last name 4. CID (not editable)
71. ValidateLaserCode Request: idNum, LaserCodePID, Name, SurName, DOB, Response: prompt mobile number
72. IAM_05: Check DOPA Request: PID, Name, SurName, DOB, NumberCard Response: ClientTransRef, ResponseCode, ResponseMesg, Code, Desc
73. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
74. Validate 1. ID Expiry date >= Today 2. ID Issue Date <= Today
75. 8. Verify ID Card
76. Title name List hard code at frontend
77. [AuditLog] IAM Proxy sheet - IAM_05 Response
78. [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
79. [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
80. IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
81. Save DOPADateTime
82. [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
83. [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
84. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
85. [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
86. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
87. Validate 1. Mobile No. start with 06, 07, 08, 09 2. Mobile No. must have number 10 digits
88. IAM_08: Send SMS OTP Template ID = "[MASKED_CODE]" "mobileType": 0 "smsType": 1 "appTypeId": 0 ...
89. SendSMSOTP Request: mobileNumber (in IA cache) Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
90. [AuditLog] IAM Proxy sheet - IAM_08 Response
91. 9. Verify Mobile No. By OTP
92. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: prompt PIN
93. [CIAM Validate] If OTP matches, then can proceed futher
94. [ActivityLog] Step 8 - NTB Onboarding - Verify Mobile using OTP - Response 8.1 - Response with PIN - Response - 8.2 - Resend OTP - In flow error Response 8.3.1 - OTP is incorrect (1 attempt) - In flow error Response 8.3.2 - OTP is incorrect (2 attempt) - In flow error Response 8.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
95. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
96. IAM_23: Create OPO profile Request: idNum, idType, Title Name Thai, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, ID Expiry Date, ID Issue Date, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion,TnCHash, PDPAFlag, PDPAPurposrCode, PDPAConsentDateTime, MobileNumber, DOPADateTime Response: ProcessInstantKey
97. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, ProcessInstantKey
98. #Cache PII data from CIAM
99. 10.1 Setup PIN
100. 10.2 Confirm PIN
101. Start Flow: Create Customer Temp Profile
102. Validate 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
103. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
104. If OPO returns error, end the flow.
105. Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
106. Validate 1. PIN and Confirm PIN is match
107. Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
108. Access Token AuthLevel = 3 CISId = Null ProcessInstantKey idenityStatus = preRegistration
109. Store Digital ID & DeviceBindingKey
110. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPIN’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
111. [AuditLog] Step 9 - NTB Onboarding - Register PIN - Response 9 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
112. [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
113. [AuditLog] Step 10 - NTB Onboarding - Bind Device - Response 10 - end of the onboarding process save state 1 - End flow - Customized error - End flow - OOTB error
114. [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
115. [AuditLog] IAM Proxy sheet - IAM_23 Response
116. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
117. Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
118. 11A.2 RTA-BeMyId Status Detail
119. [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
120. 11A.1 Display Reference Code
121. 11. Select Authentication option
122. ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
123. ‘Processing’, ‘Register’ RTAStatus = ‘Processing’ or ‘Register’
124. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
125. ‘Locked’ RTAStatus = ‘Locked’
126. 11N.2
127. 11N.1
128. Get Latest RTA Record by CI and ProcessInstantKey
129. Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
130. If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
131. Please Continue sheet ‘RTA_BeMyID’ at Step then Back to Next step Mapping FlowType
132. OPO call delete Digital ID in user device and Direct customer to Beginning point
133. Logo Image should be get from Sitecore
134. If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
135. Image should be get from Sitecore
136. Please Continue sheet ‘RTA_NDID’ at Step then Back to Next step Mapping FlowType
137. In case have no RTA Record match by CI and ProcessInstantKey Then Get All RTA List from OPO DB by CI
138. Example IDP Error code with Warning Message
139. Screen Display depends on FlowType Validation
140. Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
141. 11B.4 RTA-NDID Status Detail
142. 11B.3 Pending Authen
143. ‘Error’ (RTAStatus = ‘ERROR’)
144. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
145. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
146. ‘Processing’ RTAStatus = ‘Processing’
147. Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
148. Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
149. OPO call delete Digital ID in user device and Direct customer to Beginning point
150. User Action : Select Authentication Option from [10D.1], [10D.2]
151. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
152. Please Refer to sheet ‘RTA_NDID’ or ‘RTA_BeMyID’ depends on customer selection
153. #Save State 2 - DigitalID - AuthLevel = 3 - ProcessInstantKey - State = 2
154. Validate All Lookup data has values Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
155. Get KYC Lookup Data (Fetch Task with Data return) Request: ProcessInstantKey Response: Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
156. Customer Tap ‘Next’
157. Common Service : Lookup Data
158. Get Customer Profile from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: idNum, Thai Title Name, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, Nationality, CountryOfResidence, PlaceOfBirth, MobileNumber,ContactNumber, OfficePhoneNumber, IDAddress, MaillingAddress, OfficeAddress, Education, Occupation, TypeOfBusiness, Position, OfficeName, SourceOfAsset, SourceOfFund, IncomePermonth, AssetValue, EarningCountry1-3 Remark: To get previous input in Customer KYC Section
159. 12. Input KYC Information
160. 12.1 Personal Detail
161. 12.2 Contact Information
162. 12.3 Education & Employment
163. 12.4 Income & Assets
164. 12.5 KYC Summary
165. [ActivityLog] Step 15 - NTB Registration – Get Customer Information Response2: Fail (Log Level1)
166. If Customer Search Address
167. Common Service : Lookup Address
168. If Customer Search Country for Earning Country
169. Common Service : Lookup Country
170. Save information from Customer input to OPO DB (Temp)
171. Save KYC Information (Fetch Task) Request: ProcessInstantKey, KYC Information (each page) Response:
172. If Customer Tap ‘Next’ at Each page
173. If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
174. [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
175. If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
176. [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
177. [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
178. [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
179. If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
180. [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
181. Start Flow : Header: X-Language, X-Channel, Access Token Response: Selfie Face callback
182. Check Profile at Ping - No CIS ID - Validate Auth level = 3 - idenityStatus = preRegistration
183. [ActivityLog] Step 1 - NTB Onboarding Face Verification – Initiate - Response 1 - Response with Facial Verification - End flow - Customized error - End flow - OOTB error
184. Get CustomerProfile Temp from OPO (Instead of CIS) Request:ProcessInstantKey Response:ID, IDType, IDExpiryDate, Nationality(For Foriegner in the future), AuthenticationMethod, ReferenceId
185. IAM_24: Get profile from OPO Request: requestId, processInstanceKey Response: status
186. Face Comparison Request: selfieImage Response: Status
187. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
188. 13.1 Intro before Face Scan
189. Get IDPImage-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, ImageBase64
190. If AuthenticationMode = ‘NDID’
191. Ask for camera permission
192. Liveness checking Capture selfie image
193. [AuditLog] IAM Proxy sheet - IAM_24 Response
194. 13.2 Take a Selfie Photo for Face Scan
195. N E C
196. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
197. IAM_20 Face Comparison Request: imageFile, requestId, requestChannel Response: status, Confidencescore, bblscore
198. CIAM checks bblscore. If it equals to 3, then can proceed further
199. POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
200. 13.3 Face Scan Processing
201. If fail
202. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
203. EFM
204. If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
205. Onboard Customer Request: requestId, ProcessInstanceKey Response: cisId, cisExternalId
206. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
207. If pass face compare
208. Get Customer Profile Temp from OPO DB Objective: To Get CitizenId for CustomerSearch and Customer Profile Info for Create Profile
209. IAM_25: Onboard Customer Request: requestId, ProcessInstanceKey Response: cisId, cisExternalId
210. CIS_Wrapper(4) : Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
211. CH24
212. Get Customer Profile by ID Number Request: idNum Response: All response fields from CIS
213. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
214. [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
215. [AuditLog] in case Fail/Success Only API Inquiry without JWT token
216. Validate Response If status.code is “2005”, refer case “RMNo Has no Value” Otherwise, refer case “RMNo Has Value”
217. Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
218. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
219. [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
220. Validate Response If RiskRating < 3, Then update Risk Level, Risk Reason Code into (Customer Profile Temp of OPO DB) proceed next step to Save State Expiry. Else, return error
221. Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
222. Set segmentLevel = A13 for default segment of “Create Customer Profile-NTB”
223. Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
224. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
225. If: No RM Profile (Create CISID, Create RMNO)
226. - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
227. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
228. If identityVerifiedChannel = 002 beMyId
229. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
230. [AuditLog] in case Fail/Success Only CIS RM Update IAL
231. If: Has RM Profile (Create CISID, Update RM Profile)
232. - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
233. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
234. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
235. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
236. Check if duplicate mobile no. in CIS Profile
237. If found duplicate mobile no.
238. Delete duplicate mobile no.
239. [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
240. E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
241. Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
242. [AuditLog] in case Fail/Success Only API CREATE ACTION:
243. Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
244. Access Token AuthLevel = 3 cisId cisExternalId ProcessInstanceKey = Null idenityStatus = active
245. Update DigitalID Profile with 1. cisId 2. ProcessInstanceKey= Null 3. cisExternalId
246. [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
247. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - Response 2 - end of the onboarding process save state 3 - Response 2 - end of the onboarding process save state 3 (collect Device Info) IAM Proxy sheet - IAM_25 Response
248. [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
249. Publish Event Topic: dev.stg.efmconsumer.advice Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’: transaction success | OPO Cust Error Code: transaction fail Response:
250. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
251. E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
252. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
253. [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
254. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
255. [AuditLog] in case Fail/Success Only Backend API Update PDPA
256. If API update Host or Kafka fail, re execute fail process (retry X times)
257. Write fail payload to DB
258. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result
259. [AuditLog] - actSubType = 'RM Add Relationship'
260. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
261. [AuditLog] - actSubType = 'RM Update IAL'
262. E2: Publish Event Topic: <env>.raw.cis.party.create Event Type: party.create Remark: Add fields: BAN, SegmentLevel
263. 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
264. EOD Process (Existing) File - Batch Update RM profile (RM no., Phone number) File - Batch update relationship (RM No., CIS No.)
265. Prepare data for Call “H21: Get Daily Total Limit”. Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 4. RM Number Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now 2. RM Number from Response of “Create Customer Profile-NTB”
266. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
267. oCRM
268. If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
269. CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
270. Update Segment Level Request: CIS ID, Segment Response: All response fields from CIS
271. [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
272. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
273. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
274. TSP
275. If Update Segment Level failed,
276. OPO get EntraID (Virtual ID)
277. [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
278. Retry 3 times
279. AppsFlyer
280. Adobe SDK
281. Firebase
282. [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
283. [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
284. Remark: This is an independent process
285. CNH
286. Always Get Pushed Token from FCM by not consider on PushNotification OS
287. If Fail, then make pendingRegisterFlag is true
288. #Save State 3 - DigitalID - AuthLevel = 3 - State = 3
289. 14. Intro page to start apply product
290. Get Product Eligible [NEW] Request: CISID Response: ProductList {ProductId, ProductType, ProductNamtTH, ProductNameEN}
291. CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
292. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
293. [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
294. Get Product Eligible Request: IDType, CTCode, DOB, BBLIAL, IDPIAL, RiskLevel Response: ProductList{ProductId, ProductType, ProductNamtTH, ProductNameEN}
295. CIS_Wrapper (10): Get Customer Account Relationship Request: RM No., {customerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
296. 15. Eligible Product list
297. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
298. [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
299. Please Refer to Open eSaving Sequence Diagram at Step ‘Get Product Detail’
300. Note Mapping Request Type for Face Compare
301. 11B.4 NDID RTA status ‘Approved’
302. 11A.2 BeMyID RTA status ‘Verified’
303. CIS_Wrapper (13): Create Customer Profile-NTB POST: /customerprofile/api/v2/cis/internal/customers/new Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileIdentifications, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, contactNumber, email, agreement, consent, pdpa, channel, classification, channelProfile} Action: "CREATE_CUSTOMER_PROFILE" Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
304. CIS_Wrapper(14): Create Customer Profile-NTB (No CISID, has RMNO) Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, profile, contactNumber, agreement, identity, identifier, channel, classification, pdpa, consent, email} Action: CREATE_CUSTOMER_NTB_WITH_RM Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
305. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
306. Logo IDP Bank App *Not Existing* Need to Place Image on Sitecore for New category and has configuration to get these logoes
307. Display Refence Code with ReferenceId last 7 digits in UpperCase format
308. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
309. B_CheckRTA #SubFlow
310. B_CheckRTA
311. M_CheckRTA
312. Set Save State = 1, Expiry date = 7 days
313. Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
314. Publish Event Topic: XXXX Event Type: XXXX
315. Send DWR Profile and Access token in background
316. N_CheckRTA #SubFlow
317. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
318. B_Re-Gen RefNo
319. M_Re-Gen RTA
320. B_Cancel RTA
321. M_Cancel RTA
322. To add external id as a Firebase user id with @bbl/analytics using .setUserID()
323. CDP2: Update Identity
324. CDP3: Update Onboard success
325. Liveness Check If Yes, do face compare
326. AF1: Set ECID to customerid for AppsFlyer
327. A21: AppsFlyer initialization
328. CDP1: Update Consent Example var consents: {[keys: string]: any} = {"consents" : {"collect" : {"val": "y"}}}; Consent.update(consents)
329. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
330. CIAM binds the DPoP public key to the access token
331. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
332. Non sequential step
333. [AuditLog] IAM Proxy sheet - IAM_36 Response

### Page 6: Host_MMP Lot#2

1. OCR Server
2. CIS_Wrapper: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
3. 0. First Page
4. 1. Welcome Page
5. 2. Accept T&C
6. 3. Input CitizenID and DOB
7. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
8. If CIS profile not found or CIS status is invalid, search RM
9. 5. NTB Step Info
10. 6. Scan ID Card
11. 4. Accept PDPA Consent
12. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
13. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
14. 7. Verify ID Card
15. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
16. 8.1 Input Mobile No.
17. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
18. 8.2 Verify Mobile No.By OTP
19. 9.1 Setup PIN
20. 9.2 Verify PIN
21. Record #Save State 1
22. Authentication Option : BeMyID
23. 10 Select Verify Option
24. H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(48hr from config), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
25. H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
26. 10A.1 Display Reference Code
27. 10A.2 Authentication Success
28. RTA Status = ‘Verified’
29. H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
30. Authentication Option : NDID
31. H8: Get IDP List URL: POST /NDIDSwagger/RPServices/utility/idp_list Request: NameSpace = ‘citizen_id’, Citizen ID, Min IAL=2.3, Min AAL=2.2 Response: Node ID, Max IAL, Max AAL, Preferred IDP Flag, Industry Code Company Code, Thai Marketing Name, English Marketing Name, Thai Proxy or Subsidiary Name,English Proxy or Subsidiary Name, Role, Running
32. 10B.2 Select Provider
33. H9: GenerateRTA-NDID URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
34. 10B.3 Request NDID
35. H11: Close RTA-NDID URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
36. 10B.4 NDID RTA status ‘Approved’
37. H10: Get RTA Status-NDID URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
38. 11.1 Personal Detail
39. 11.2 Contact Information
40. 11.3 Education & Employment
41. 11.4 Income & Assets
42. 11.5 KYC Summary
43. 12.1 Intro before Face Scan
44. H10: Get RTA Status-NDID URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
45. Ask for camera permission
46. 12.2 Take a Selfie Photo for Face Scan
47. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
48. 12.3 Face Scan Processing
49. H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
50. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
51. Set segmentLevel = A13 for default segment of “Create Customer Profile-NTB”
52. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
53. If: No CIS ID, No RM Profile
54. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
55. 13. Intro page to start apply product
56. H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
57. Record #Save State 3
58. If: No CIS ID, Has RM Profile
59. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
60. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
61. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
62. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
63. EOD Process H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
64. Prepare data for Call “H21: Get Daily Total Limit”. Fields from Response of “Create Customer Profile-NTB” 1. RM Number Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now
65. H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
66. If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
67. 14. Intro page to start apply product
68. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
69. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
70. 15. Eligible Product list
71. Please Refer to Document [NCBD] Open eSavings Flow Host Requirement V0.1
72. Validate Response Customer has no RM Profile
73. Validate Response Detection Score >= 0.6
74. Validate Response Response Code = 0 and Desc = ‘สถานะปกติ’
75. Validate Response Response should contains only Datetime and no ‘suspiciousCustomerInfo’
76. Verify OTP
77. 1. Set Up PIN 2. Create Temp Profile 3. Create Save state #1
78. Validate Response HTTP code = 200 and responseCode = 000
79. Validate Response HTTP code = 200 and responseCode = 000
80. Validate Response 1. HTTP code = 200 and responseCode = 000 2. Check RTA Status
81. Validate Response Filter Role = ‘IDP’ only
82. Validate Response Http code = 202 and RequestId has value
83. Validate Response Http code = 202
84. Validate Response 1. Http code = 202 2. Check ndid_status and cust_action
85. Validate Response 1. Http code = 202 2. Retrieve customer_biometric
86. Validate Response FaceCompare result
87. Validate Response RMNo. Has value or not

### Page 7: RTA_BeMyID (MMP Lot#2)

1. #Save State 1 - DigitalID - AuthLevel = -1 - ProcessInsantKey - State = 1
2. 10. Select Authentication option
3. Get Customer Profile from cache
4. Get Latest RTA Record by CI and ProcessInstantKey
5. Genereate RTA-BeMyId Request: ProcessInstantKey Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, MachineName, RTAApprovedDateTime, ServicePointUrl
6. Validate RTA Record If [RTAStatus = ‘Register’ or ‘Processing’] then,Return General Error Else, proceed next step to call Generate CustomerRefNo
7. Generate CustomerRefNo 7 digits - Bank Code (2 digits) : Fixed value ‘02’ - Partner Code (2 digits) : Fixed value ‘04’ - Running number (3 digits)
8. Insert New Running RefCode Per CI
9. Generate ReferenceId format: B_Channel_YYYYMMDD_GUID
10. H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType (‘TC01’), durationOfTimeout(48hr from config), partnerId (‘04’) Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
11. Validate Response If (H6) HTTP response code = 200 and responseCode = 000 Then, Insert DB with ReferenceId, IdNum, ProcessInstantKey, RTAId, RTACreateDateTime, RTAStatus = (status), RTAExpiryDateTime = (RTACreateDateTime+Duration Of Timeout)
12. [AuditLog] Step 4 - NTB Registration - Create BeMyId RTA Response1: Success Response2: Fail
13. 10A.1 Display Reference Code
14. Cancel RTA-BeMyId Request: ProcessInstantKey, ReferenceId Response: FlowType
15. Customer Action :
16. If Customer Action: Tap ‘Change Method’
17. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey *Remark: To get CustomerRefNo
18. Proceed count down time Calculated from ExpiryDateTime – DateTime.Now
19. Validate RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to next step H6: GenerateRTA-BeMyID Else if RTAStatus = ‘Locked’ or ‘Expired’ or ‘Rejected’ Then Skip H6 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
20. Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
21. Update DB with UpdateDateTime, RTA Status = ‘Cancelled’
22. H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
23. 10. Select Authentication option
24. 10N.2
25. 10N.1
26. Get All RTA List from OPO DB by CI
27. [AuditLog] Step 5 - NTB Registration – Cancel BeMyId RTA Response1: Success Response2: Fail
28. Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
29. Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
30. [ActivityLog] Step 5 - NTB Registration – Cancel BeMyId Request Response1: Success (Log level2) Response2: Fail (Log Level1)
31. Get RTA Status-BeMyId Request: ProcessInstantKey, ReferenceId, Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, RefCode, MachineName, RTAApprovedDateTime, ServicePointUrl
32. If Customer Action: Tap ‘I’ve Enter My code’
33. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey
34. 10A.1 Display reference code
35. 10A.2 RTA-BeMyId Status Detail
36. H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
37. ‘Verified’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘N’)
38. ‘Processing’ RTAStatus = ‘Processing’
39. ‘Register’ RTASTatus = ‘Register’
40. ‘Expired’ RTAStatus = ‘Expired’
41. ‘Rejected’ RTAStatus = ‘Rejected’
42. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
43. ‘Locked’ RTAStatus = ‘Locked’
44. Validate RTAStatus If RTAStatus = ‘Register’ or ‘Processing’ then, proceed next step to call (H7): InquiryRTA-BeMyID
45. 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
46. [AuditLog] Step 6 - NTB Registration – Check BeMyId RTA Status Response1: Success Response2: Fail
47. RTA Status: ‘Verified’
48. Get Customer Profile from OPO DB
49. User Press ‘OK’, pop-up will be closed and still being in [10A.1] Display Reference Code
50. OPO call delete Digital ID in user device and Direct customer to Beginning point
51. Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H7 as below: If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If ID Number is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If Issue Date is match then Set IssueDate_PassValidateFlag = ‘Y’ Else IssueDate_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
52. CTA Scenario
53. Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
54. After customer Tap at this CTA, Continue service at Tap ‘NTB_Registration’
55. Mapping Response ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, MachineName, RTAApprovedDateTime, ServicePointUrl (from Configuration)
56. [ActivityLog] Step 7 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
57. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : Null NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_DipChip’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
58. Please Refer to sheet ‘NTB Registration’ to continue Save State 2 Process
59. B_CheckRTA #SubFlow
60. New Entry

### Page 8: RTA_NDID (Lot#2)

1. #Save State 1 - DigitalID - AuthLevel = -1 - ProcessInsantKey - State = 1
2. 10. Select Authentication option
3. Get NDID T&C Content Request: language, type =”NDID_TC” Response: version, ndidcontentUrl
4. Consent service CMS
5. Consent DB CMS
6. Consent Blob CMS
7. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NDID}/doc-type/{docTypeCode4=NTNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version
8. [AuditLog] Step 8 - NTB Registration – Get NDID TC Response1: Success Response2: Fail
9. Update NDID T&C Acceptance (Fetch Task) Request: ProcessInstantKey, ndidConsentVersion, ndidConsentDateTime, ndidConsentFlag Response:
10. 10B.1 Accept NDID T&C
11. Update NDID T&C Acceptance
12. [AuditLog] Step 9 - NTB Registration – NDID TC Acceptance Response1: Success Response2: Fail
13. Example: IDP Whitelist Configuration [ { "company_code": "002", "industryCode": "001", "app_name_thai": "บัวหลวง เอ็มแบงก์กิ้ง", "app_name_eng": "Bualuang mBanking" }, { "company_code": "004", "industryCode": "001", "app_name_thai": "K Plus", "app_name_eng": "K Plus" } ]
14. H8: Get IDP List [New Service] URL: POST /NDIDSwagger/RPServices/utility/idp_list Request: NameSpace = ‘citizen_id’, Citizen ID, Min IAL=2.3, Min AAL=2.2 Response: Node ID, Max IAL, Max AAL, Preferred IDP Flag, Industry Code Company Code, Thai Marketing Name, English Marketing Name, Thai Proxy or Subsidiary Name,English Proxy or Subsidiary Name, Role, Running
15. Get IDP List (Fetch Task with Data return) Request: ProcessInstantKey Response: IDPList {NodeID, PreferredIDPFlag, IndustryCode, CompanyCode, appNameTh, appNameEn, Role, Running, IDPBankLogoUrl}
16. Validate IDP List If IDP has Preferred IDP Flag = ‘Y’ Then display IDP in section ‘Enrolled’ Elese, display in Section ‘Not Enrolled’
17. [AuditLog] Step 10 - NTB Registration – GetIDPBankList Response1: Success Response2: Fail
18. 1. Filter IDP Only Return from Role=”IDP” 2. Check IDP Whitelist Configuration Return only IDP List that match in IDP whitelist configuration and sort by company_code asending 3. Mapping Additional Response ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode
19. Genereate RTA-NDID (Fetch Task with Data return) Request: idp_id_list Response: ReferenceId, RTAStatus, RTACreateDateTime, RTAExpiryDateTime, appNameTh, appNameEn , IDPBankLogoUrl
20. 10B.2 Select Provider
21. “ขอยืนยันตัวตนเพื่อใช้บริการกับธนาคารกรุงเทพ และประสงค์ให้ส่งข้อมูลประกอบการยืนยันตัวตนพร้อมรูปถ่ายให้ธนาคาร” concat with string “(รหัสอ้างอิง: { Last 8 digits of ReferenceId with Upper case })” Example: ขอยืนยันตัวตนเพื่อใช้บริการกับธนาคารกรุงเทพ และประสงค์ให้ส่งข้อมูลประกอบการยืนยันตัวตนพร้อมรูปถ่ายให้ธนาคาร รหัสอ้างอิง: RE7H05TS
22. 1. Get RTA List from OPO DB by CI If Count of ReferendId start with ‘NCBD_XXX’ >= 10 then, return Error Else continue Next to Get Latest RTA 2. Get Latest RTA Record by CI and ProcessInstantKey If RTAStatus = ‘Processing’ Then, Return General Error Else, proceed next step to call Generate ReferenceId
23. Fields in orange highlight should be in configuration
24. H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
25. Generate ReferenceId format: NCBD_YYYYMMDD_GUID
26. Navigate to 10. Select Authentication option
27. Validate Response If (H9) HTTP response code = 202 and RequestId has value Then, Insert DB with ReferenceId, RequestId, IDNum, ProcessInstantKey, UpdateDateTime, RTAStatus = ‘Processing’, RTACreateDateTime, CompanyCode, IndustryCode, appNameTh, appNameEn
28. [AuditLog] Step 11 - NTB Registration – Create NDID RTA Response1: Success Response2: Fail
29. Mapping Response ReferenceId, RTAStatus = ‘Processing’, RTACreateDateTime (default to RequestDatetime), RTAExpiryDateTime (default to RequestDatetime + request_timeout), IDPBankLogoUrl(PrefixURL + CompanyCode), appNameTh = app_name_thai, appNameEn = app_name_eng
30. Customer Action :
31. Cancel RTA-NDID Request: ProcessInstantKey, ReferenceId, Response: FlowType
32. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey
33. If Customer Action: Tap ‘Change Method’
34. 10B.3 Pending Authen
35. Proceed count down time Calculated from ExpiryDateTime – DateTime.Now
36. H11: Close RTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
37. Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
38. Display Refence Code with ReferenceId last 7 digits in UpperCase format
39. Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
40. Validate Response If (H9) HTTP response code = 202 Update DB with UpdateDateTime, RTAStatus = ‘Cancelled’
41. 10. Select Authentication option
42. 10N.2
43. 10N.1
44. [AuditLog] Step 12 - NTB Registration – Cancel NDID RTA Response1: Success Response2: Fail
45. Get All RTA List from OPO DB by CI
46. Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
47. Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
48. If Customer Action: Tap ‘I’ve already authenticated’
49. 1. Get Customer Profile 2. Get Latest RTA Record by CI and ProcessInstantKey
50. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
51. Get RTA Status-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl
52. Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed next step to call (H10): Get RTA Status-NDID
53. [AuditLog] Step 13 - NTB Registration – Check NDID RTA Status Response1: Success Response2: Fail
54. Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
55. Validate RTA Expiry If Not Expired then, Proceed further Else, Update DB with UpdateDateTime, RTAStatus = ‘Expired’
56. 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
57. Get OPO User Temp Profile
58. If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
59. Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H10 as below: #To Be Revise If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If English First Name is match then Set FirstNameEN_PassValidateFlag = ‘Y’ Else FirstNameEN_PassValidateFlag = ‘N’ If English Last Name is match then Set LastNameEN_PassValidateFlag = ‘Y’ Else LastNameEN_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If ID is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
60. 10B.3 Pending Authen
61. 10B.4 RTA-NDID Status Detail
62. ‘Processing’ RTAStatus = ‘Processing’
63. ‘Expired’ RTAStatus = ‘Expired’
64. ‘Rejected’ RTAStatus = ‘Rejected’
65. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
66. ‘Error’ (RTAStatus = ‘Error’)
67. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
68. Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
69. Mapping Response ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, RTAApprovedDateTime, appNameTh, appNameEn, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl = ‘PrefixURL’ (from config) + CompanyCode
70. OPO call delete Digital ID in user device and Direct customer to Beginning point
71. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
72. [ActivityLog] Step 14 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
73. Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_NDID’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
74. Please Refer to sheet ‘NTB Registration’ to continue #Save State 2 Process
75. New Entry
76. N_CheckRTA #SubFlow

### Page 9: State_Handling(MMP)

1. Sequence Diagram - NTB Registration : State Handling This will be used for NTB flow to route to destination page for each customer scenario
2. Splash Screen
3. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page Else if
4. Welcome & Orientation
5. No Digital ID
6. Initiate Device Login Request: {"app_version_proof": "<signed_app_version_JWS>"} -> Sign the DBA with the device-binding private key, X-DPoP-Token Response: authId, userId, challenge
7. 0A. First Page (No Digital ID)
8. Validation - Maintenance check - Validate DPoP proof - Validate DBA signature - Extract signed app version from DBA payload, verify it using the signature DPoP public key - Minimum OS version and Force upgrade app
9. Check CIAM Channel Status - Locked => PIN locked alert - Active => Proceed next step
10. Continue to Customer Enrollment Journey
11. Device Binding Authenticate Request: signed JWT Response: Access Token, Refresh Token and ID Token
12. Sign challenge with private key
13. 0B. First Page (Has Digital ID)
14. Validation - Validate DPOP proof - Validate Recommend app version
15. PIN Authenticate Request: PIN, X-DPoP-Token Response: Access Token, Refresh Token and ID Token
16. CIAM checks 1. Validate DPoP proof - validate auth 2. Access Token is valid or not 3. Channel status - Locked > PIN locked alert - Active > Go to next step 4. PIN is valid or not
17. JWT Token (Auth Level =3)
18. JWT Token 1. Auth Level = 3 2. CIS ID = Null 3. identityStatus = preRegistration 4. ProcessInstantKey
19. Start Flow: Get State Request: ProcessInstantKey Response: State
20. 1. Get Current Save State 2. Validate Save state Expiry à If Save state is not expired, Then Return currentState à Else if Save state is expired or could not find save state, then Return error ERR_OPO_COM_034
21. Validate Response If currentState in state 1, then continue to call Get RTA List from OPO DB Else if currentState in state 2, then continue to call Get KYC Lookup Data
22. If Save State = 1 then, direct customer to Get RTA List from OPO DB
23. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
24. If Save State = 2 then, direct customer to KYC
25. #Save State 2 - DigitalID - AuthLevel = 3 - ProcessInstantKey - State = 2
26. If Save State = 3 then, direct customer to product origination
27. #Save State 3 - DigitalID - AuthLevel = 3 - ProcessInstantKey - State = 3

### Page 10: State_Handling(Post-MMP)

1. POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3
2. Sequence Diagram - NTB Registration : State Handling This will be used for NTB flow to route to destination page for each customer scenario
3. Splash Screen
4. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page Else if
5. Welcome & Orientation
6. No Digital ID
7. Initiate Device Login Request: {"app_version_proof": "<signed_app_version_JWS>"} -> Sign the DBA with the device-binding private key, X-DPoP-Token Response: authId, userId, challenge
8. 0A. First Page (No Digital ID)
9. Validation - Maintenance check - Validate DPoP proof - Validate DBA signature - Extract signed app version from DBA payload, verify it using the signature DPoP public key - Minimum OS version and Force upgrade app
10. Check CIAM Channel Status - Locked => PIN locked alert - Active => Proceed next step
11. Continue to Customer Enrollment Journey
12. Device Binding Authenticate Request: signed JWT Response: Access Token, Refresh Token and ID Token
13. Sign challenge with private key
14. 0B. First Page (Has Digital ID)
15. Validation - Validate DPOP proof - Validate Recommend app version
16. Darwinium
17. Existing Device Profiling of Logon Process #TBC
18. [ActivityLog] Risk Journey (Fraud Detection - Darwinium) - Response 1 - Fraud Detection - Include geoLocation (Latitude, Longitude) - End flow - Customized error - End flow - OOTB error
19. PIN Authenticate Request: PIN, X-DPoP-Token Response: Access Token, Refresh Token and ID Token
20. CIAM checks 1. Validate DPoP proof - validate auth 2. Access Token is valid or not 3. Channel status - Locked > PIN locked alert - Active > Go to next step 4. PIN is valid or not
21. JWT Token (Auth Level =3)
22. Start Flow: Get State Request: ProcessInstantKey Response: State
23. JWT Token 1. Auth Level = 3 2. CIS ID = Null 3. identityStatus = preRegistration 4. ProcessInstantKey
24. 1. Get Current Save State 2. Check CIS ID in customer prospect table à If CIS ID have value, return error ERR_OPO_NTB_043. à Otherwise, continue to proceed No.3 3. Validate Save state Expiry à If Save state is not expired, Then Return currentState à Else if Save state is expired or could not find save state, then Return error ERR_OPO_COM_034
25. Validate Response If currentState in state 1, then continue to call Get RTA List from OPO DB Else if currentState in state 2, then continue to call Get KYC Lookup Data
26. If Save State = 1 then, direct customer to Get RTA List from OPO DB
27. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
28. If Save State = 2 then, direct customer to KYC
29. #Save State 2 - DigitalID - AuthLevel = 3 - ProcessInstantKey - State = 2
30. Publish Event Topic: XXXX Event Type: XXXX
31. Send DWR Profile and Access token in background
32. Send IAM_36: Digital Risk ( Darwinium) Request: cisId, device_signature[ver_1].identifier, profiling.source, profiling.ios.os_version, profiling.android.build.version_release, ...
33. Verify Profile blob against Darwinium server Request: Profile blob Response: Risk score and data
34. [AuditLog] IAM Proxy sheet - IAM_36 Response

### Page 11: [BK] NTB_Registration (MMP Lot#2)

1. Related Hosts 1. RM 2.SmartCard 3. DOPA-Gateway 4. CH24 5. SMS Gateway 6. PWS 7. BLDG-NDID 8. FARA 9. SAS 10. ST 11. DGEN
2. Sequence Diagram - NTB Registration
3. 1 First Page (No Digital ID)
4. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
5. 2. Welcome Page
6. TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
7. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
8. Ask Permission for - Activity tracking - Push notification
9. Cache allowPushFlag
10. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
11. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 1 - Responds back with a DeviceProfileCallback - Response 2 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
12. Submit device meta data Request: metadata, location, message Response: T&C URL
13. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, TandCUrl
14. 3. Accept T&C
15. System Token issued by PING
16. Auth_ID token (10minutes expired)
17. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
18. Auth ID token – return in every call, change to the new one every call (60 minutes expired)
19. [AuditLog] Step 2 - Customer Enrollment Welcome Page - IAM_01 Response
20. Auth ID token in the request
21. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
22. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
23. 4. Input CitizenID, DoB & Mobile
24. Check sum and format of Citizen ID
25. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
26. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
27. Private API - Group System token issued by Ping
28. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
29. StartProcessByCID Request: citizen ID, DOB, idType Response: citizen ID, DOB, prompt laserCode
30. If CIS profile not found or CIS status is invalid, search RM
31. CIAM logic to separate flows Has CIS -> Reactivate No CIS, Has RM -> ETB No CIS, No RM -> NTB
32. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
33. [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
34. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - IAM_02 Response
35. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4.1 - Response Reactivation - Response 4.1 - Response NTB - Response 4.3 - go back to T&C - End flow - Customized error - End flow - OOTB error
36. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPAFULL}/asset-type/{assetType=JSON} Response: blobData, mimeType, version
37. 5. Accept PDPA Consent
38. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
39. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - IAM_10 Response
40. Save Customer PDPA Acceptance (AcceptanceFlag, ConsentDate, ConsentTypeValue)
41. 6. NTB Step
42. [ActivityLog] Step 5 - NTB Onboarding - Full PDPA Consent - Response 5.1 - Response with OCR - End flow - OOTB error
43. FARA (OCR Server)
44. Resolution 800 pixels
45. 7. Scan ID Card
46. Submit OCR Request: image base 64 binary Response: English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date *Remark Return value for Thai Title, English Title, Thai First Name, Thai Last Name, ID Number only
47. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
48. IAM_22 (new): Submit data to OCR Request: image base 64 binary Response: Detection Score, ID Number, Thai Birth Date, Thai Title, Thai First Name, Thai Last Name, expiryDate, issuerDate, gender, EN Title, EN First Name, EN Last Name, DOB
49. [AuditLog] Step 6 - NTB Onboarding - Submit data to OCR - IAM_22 Response
50. [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
51. [CIAM Validate] 1. Detection Score >= 0.8 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
52. Prefill data from OCR 1. TitleNameTH / TitleNameEN 2. TH First name 3. TH Last name 4. CID (not editable)
53. ValidateLaserCode Request: idNum, LaserCodePID, Name, SurName, DOB, Response: prompt mobile number
54. IAM_05: Check DOPA (5 Fields) Request: PID, Name, SurName, DOB, LaserCode Response: ClientTransRef, ResponseCode, ResponseMesg
55. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
56. Validate 1. ID Expiry date >= Today 2. ID Issue Date <= Today
57. 8. Verify ID Card
58. Title name List hard code at frontend
59. [AuditLog] Step 7 - NTB Onboarding - Laser Code - IAM_05 Response
60. [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
61. [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
62. IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
63. Save DOPADateTime
64. [CIAM Validate] CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
65. [AuditLog] in case Fail Only Step 7 - NTB Onboarding - Laser Code - IAM_06 Response
66. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
67. [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
68. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
69. Validate 1. Mobile No. start with 06, 07, 08, 09 2. Mobile No. must have number 10 digits
70. SendSMSOTP Request: mobileNumber (in IA cache) Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
71. IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
72. [AuditLog] Step 7 - NTB Onboarding - Laser Code - IAM_08 Response
73. 9. Verify Mobile No. By OTP
74. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: prompt PIN
75. [CIAM Validate] If OTP matches, then can proceed futher
76. [ActivityLog] Step 8 - NTB Onboarding - Verify Mobile using OTP - Response 8.1 - Response with PIN - Response - 8.2 - Resend OTP - In flow error Response 8.3.1 - OTP is incorrect (1 attempt) - In flow error Response 8.3.2 - OTP is incorrect (2 attempt) - In flow error Response 8.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
77. IAM_23 (new): Create OPO profile Request: idNum, idType, Title Name Thai, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, ID Expiry Date, ID Issue Date, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion,TnCHash, PDPAFlag, PDPAPurposrCode, PDPAConsentDateTime, MobileNumber, DOPADateTime Response: ProcessInstantKey
78. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, ProcessInstantKey
79. #Cache PII data from CIAM
80. 10.1 Setup PIN
81. 10.2 Confirm PIN
82. Start Flow: Create Customer Temp Profile
83. Validate 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
84. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
85. If OPO returns error, end the flow.
86. Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
87. Validate 1. PIN and Confirm PIN is match
88. Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
89. Access Token AuthLevel = 3 CISId = Null ProcessInstantKey idenityStatus = preRegistration
90. Store Digital ID & DeviceBindingKey
91. [AuditLog] (Fail Only) Step 1 – NTB Registration – Create Customer Profile Temp
92. [AuditLog] Step 9 - NTB Onboarding - Register PIN - Response 9 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
93. [AuditLog] Step 9 - NTB Onboarding - Register PIN - IAM_23 Response
94. [AuditLog] Step 10 - NTB Onboarding - Bind Device - Response 10 - end of the onboarding process save state 1 - End flow - Customized error - End flow - OOTB error
95. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
96. Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
97. 11A.2 RTA-BeMyId Status Detail
98. 11A.1 Display Reference Code
99. 11. Select Authentication option
100. ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
101. ‘Processing’, ‘Register’ RTAStatus = ‘Processing’ or ‘Register’
102. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
103. ‘Locked’ RTAStatus = ‘Locked’
104. 11N.2
105. 11N.1
106. Get Latest RTA Record by CI and ProcessInstantKey
107. Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
108. If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
109. Please Continue sheet ‘RTA_BeMyID’ at Step then Back to Next step Mapping FlowType
110. OPO call delete Digital ID in user device and Direct customer to Beginning point
111. Logo Image should be get from Sitecore
112. If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
113. Image should be get from Sitecore
114. Please Continue sheet ‘RTA_NDID’ at Step then Back to Next step Mapping FlowType
115. In case have no RTA Record match by CI and ProcessInstantKey Then Get All RTA List from OPO DB by CI
116. Example IDP Error code with Warning Message
117. Screen Display depends on FlowType Validation
118. Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
119. 11B.4 RTA-NDID Status Detail
120. 11B.3 Pending Authen
121. ‘Error’ (RTAStatus = ‘ERROR’)
122. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
123. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
124. ‘Processing’ RTAStatus = ‘Processing’
125. Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
126. Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
127. OPO call delete Digital ID in user device and Direct customer to Beginning point
128. User Action : Select Authentication Option from [10D.1], [10D.2]
129. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
130. Please Refer to sheet ‘RTA_NDID’ or ‘RTA_BeMyID’ depends on customer selection
131. #Save State 2 - DigitalID - AuthLevel = -1 - ProcessInstantKey - State = 2
132. Validate All Lookup data has values Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
133. Get KYC Lookup Data (Fetch Task with Data return) Request: ProcessInstantKey Response: Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
134. Customer Tap ‘Next’
135. Common Service : Lookup Data
136. Get Customer Profile from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: idNum, Thai Title Name, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, Nationality, CountryOfResidence, PlaceOfBirth, MobileNumber,ContactNumber, OfficePhoneNumber, IDAddress, MaillingAddress, OfficeAddress, Education, Occupation, TypeOfBusiness, Position, OfficeName, SourceOfAsset, SourceOfFund, IncomePermonth, AssetValue, EarningCountry1-3 Remark: To get previous input in Customer KYC Section
137. 12. Input KYC Information
138. 12.1 Personal Detail
139. 12.2 Contact Information
140. 12.3 Education & Employment
141. 12.4 Income & Assets
142. 12.5 KYC Summary
143. If Customer Search Address
144. Common Service : Lookup Address
145. If Customer Search Country for Earning Country
146. Common Service : Lookup Country
147. Save information from Customer input to OPO DB (Temp)
148. Save KYC Information (Fetch Task) Request: ProcessInstantKey, KYC Information (each page) Response:
149. If Customer Tap ‘Next’ at Each page
150. If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
151. If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
152. [ActivityLog] (Sucess/Fail) Step 18 - NTB Registration – Save KYC Info
153. If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
154. Start Flow : Header: X-Language, X-Channel, Access Token Response: Selfie Face callback
155. Check Profile at Ping - No CIS ID - Validate Auth level = 3 - idenityStatus = preRegistration
156. Get CustomerProfile Temp from OPO (Instead of CIS) Request:ProcessInstantKey Response:ID, IDType, IDExpiryDate, Nationality(For Foriegner in the future), AuthenticationMethod, ReferenceId
157. IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
158. Face Comparison Request: selfieImage Response: Status
159. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
160. 13.1 Intro before Face Scan
161. Get IDPImage-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, ImageBase64
162. If AuthenticationMode = ‘NDID’
163. Ask for camera permission
164. Liveness checking Capture selfie image
165. [AuditLog] Step 1 - NTB Onboarding Face Verification – Initiate - IAM_24 Response
166. 13.2 Take a Selfie Photo for Face Scan
167. N E C
168. IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
169. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
170. CIAM checks bblscore. If it equals to 3, then can proceed further
171. 13.3 Face Scan Processing
172. If fail
173. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error - IAM_20 Response
174. If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
175. Onboard Customer Request: ProcessInstantKey, requestId Response: CISID Remark:
176. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
177. If pass face compare
178. Get Customer Profile Temp from OPO DB Objective: To Get CitizenId for CustomerSearch and Customer Profile Info for Create Profile
179. IAM_25 (new): Onboard Customer Header: ProcessInstantKey Request: requestId Response: cisId
180. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
181. Customer Search by Citizen ID Request: idNum Response: RMNo, CitizenId, RMNo
182. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: RMNo, CitizenId, DoB
183. [AuditLog] (Fail Only) Step 19 - NTB Registration – Customer Search RM
184. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
185. Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
186. If RMNo. Has value
187. CIS_Wrapper (2) : Get Customer Profile by RM No POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: RMNO, {customerProfile, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, customerProfileEdd} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
188. Get Customer Profile by RMNo Request: RMNo. Response: All response fields from CIS
189. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
190. [AuditLog] (Fail Only) Step 20 - NTB Registration – Get Customer Profile
191. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
192. Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
193. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
194. [AuditLog] (Fail Only) Step 21 - NTB Registration – Check AML Risk Rating
195. Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
196. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
197. Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
198. Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
199. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
200. If: No RM Profile (Create CISID, Create RMNO)
201. - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
202. Validate Response No CIS, No RM -> Call Next Process H14:Create Customer Profile at RM No CIS, Has RM -> Call Next Process H15:Update Customer KYC at RM
203. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
204. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
205. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Create RMNO' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/echannel/profile", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
206. If: Has RM Profile (Create CISID, Update RM Profile)
207. - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
208. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
209. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
210. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
211. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Update CustomerProfile' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/profiles/new-account-compliance", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
212. Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
213. Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
214. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - Response 2 - end of the onboarding process save state 3 - IAM_25 Response
215. Access Token AuthLevel = 3 CIS ID ProcessInstantKey = Null idenityStatus = active
216. Update DigitalID Profile with 1. CIS ID 2. ProcessInstantKey= Null
217. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = <env>.raw.cis.party.create - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
218. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
219. [AuditLog] (Fail Only) Step 22 - NTB Registration – Create CIS Profile
220. E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
221. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = <env>.raw.cis.party.create/ <env>.raw.cis.party.update - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
222. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
223. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
224. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
225. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
226. If API update CustomerProfileRelAdd fail
227. E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
228. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
229. Check if duplicate mobile no. in CIS Profile
230. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = Map <Kafka topic name> - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
231. If found duplicate mobile no.
232. Delete duplicate mobile no.
233. E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
234. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = Map <Kafka topic name> - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
235. [QA] CIS will update to KAFKA then IAM subscribe for recheck flag hasMobile No.
236. E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
237. EOD Process (Existing) File - Batch Update RM profile (RM no., Phone number) File - Batch update relationship (RM No., CIS No.)
238. H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
239. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = n/a - alternateIdType = n/a - alternateId = n/a - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = `Batch’ - actType = 'Batch from CIS' - actSubType = 'Batch Add Relationship to RM'/ 'Batch Update Mobile Number to RM' - actStatus = Batch file transfer result (Exit Code) - errorCode = batch_job_execution.exit_code - errorMessage = batch_job_execution.exit_message (first 200 char) - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = แต่ละ step ของ Batch
240. TSP
241. Apigee (engagement)
242. OPO get EntraID (Virtual ID)
243. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
244. Retry 3 times
245. Remark: This is an independent process
246. [ActivityLog] (Sucess/Fail) Step 23 - NTB Registration – Create TSP Profile
247. Check isAllowPushNoti flag in cache align on setting in device
248. CNH
249. Get Pushed Token from FCM
250. If allowPushFlag is ‘Y’, Else skip process
251. #Save State 3 - DigitalID - AuthLevel = 3 - State = 3
252. 14. Intro page to start apply product
253. Get Product Eligible [NEW] Request: CISID Response: ProductList {ProductId, ProductType, ProductNamtTH, ProductNameEN}
254. CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
255. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
256. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
257. [AuditLog] (Fail Only) Step 24 - NTB Registration – Get Customer Profile
258. Get Product Eligible Request: IDType, CTCode, DOB, BBLIAL, IDPIAL, RiskLevel Response: ProductList{ProductId, ProductType, ProductNamtTH, ProductNameEN}
259. CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
260. 15. Eligible Product list
261. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
262. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
263. [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List
264. Please Refer to Open eSaving Sequence Diagram at Step ‘Get Product Detail’
265. Note Mapping Request Type for Face Compare
266. 11B.4 NDID RTA status ‘Approved’
267. 11A.2 BeMyID RTA status ‘Verified’
268. CIS_Wrapper (3): Create Customer Profile-NTB POST: /customerprofile/api/v2/cis/internal/customers/new Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileIdentifications, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, contactNumber, email, agreement, consent, pdpa, channel, classification} Action: "CREATE_CUSTOMER_PROFILE" Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
269. CIS_Wrapper(3): Create Customer Profile-NTB (No CISID, has RMNO) Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, profile, contactNumber, agreement, identity, identifier, channel, classification, pdpa, consent, email} Action: CREATE_CUSTOMER_NTB_WITH_RM Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
270. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
271. Logo IDP Bank App *Not Existing* Need to Place Image on Sitecore for New category and has configuration to get these logoes
272. Display Refence Code with ReferenceId last 7 digits in UpperCase format
273. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
274. B_CheckRTA #SubFlow
275. B_CheckRTA
276. M_CheckRTA
277. Set Save State = 1, Expiry date = 7 days
278. Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
279. N_CheckRTA #SubFlow
280. B_Re-Gen RefNo
281. M_Re-Gen RTA
282. B_Cancel RTA
283. M_Cancel RTA
284. Liveness Check If Yes, do face compare
285. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version

### Page 12: Host

1. OCR Server
2. CIS_Wrapper: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
3. 0. First Page
4. 1. Welcome Page
5. 2. Accept T&C
6. 3. Input CitizenID and DOB
7. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
8. If CIS profile not found or CIS status is invalid, search RM
9. 5. NTB Step Info
10. 6. Scan ID Card
11. 4. Accept PDPA Consent
12. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
13. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
14. 7. Verify ID Card
15. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
16. 8.1 Input Mobile No.
17. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
18. 8.2 Verify Mobile No.By OTP
19. 9.1 Setup PIN
20. 9.2 Verify PIN
21. Record #Save State 1
22. Authentication Option : BeMyID
23. 10 Select Verify Option
24. H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(48hr from config), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
25. H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
26. 10A.1 Display Reference Code
27. 10A.2 Authentication Success
28. RTA Status = ‘Verified’
29. H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
30. Authentication Option : NDID
31. H8: Get IDP List [New Service] URL: POST /NDIDSwagger/RPServices/utility/idp_list Request: NameSpace = ‘citizen_id’, Citizen ID, Min IAL=2.3, Min AAL=2.2 Response: Node ID, Max IAL, Max AAL, Preferred IDP Flag, Industry Code Company Code, Thai Marketing Name, English Marketing Name, Thai Proxy or Subsidiary Name,English Proxy or Subsidiary Name, Role, Running
32. 10B.2 Select Provider
33. H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
34. 10B.3 Request NDID
35. H11: Close RTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
36. 10B.4 NDID RTA status ‘Approved’
37. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
38. 11.1 Personal Detail
39. 11.2 Contact Information
40. 11.3 Education & Employment
41. 11.4 Income & Assets
42. 11.5 KYC Summary
43. 12.1 Intro before Face Scan
44. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
45. Ask for camera permission
46. 12.2 Take a Selfie Photo for Face Scan
47. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
48. 12.3 Face Scan Processing
49. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
50. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
51. If RMNo. Has value
52. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Numbe, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
53. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
54. If: No CIS ID, No RM Profile
55. 13. Intro page to start apply product
56. H14: Create Customer Profile at RM [NewService] POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
57. Record #Save State 3
58. If: No CIS ID, Has RM Profile
59. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
60. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
61. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
62. EOD Process H14: File - Batch Update RM profile (RM no., Phone number) H15: File - Batch update relationship (RM No., CIS No.)
63. 13. Intro page to start apply product
64. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
65. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
66. 14. Eligible Product list
67. Please Refer to Document [NCBD] Open eSavings Flow Host Requirement V0.1
68. Mapping Response to Send in H13 in case Customer Already has RM Profile
69. Validate Response Customer has no RM Profile
70. Validate Response Detection Score >= 0.6
71. Validate Response Response Code = 0 and Desc = ‘สถานะปกติ’
72. Validate Response Response should contains only Datetime and no ‘suspiciousCustomerInfo’
73. Verify OTP
74. 1. Set Up PIN 2. Create Temp Profile 3. Create Save state #1
75. Validate Response HTTP code = 200 and responseCode = 000
76. Validate Response HTTP code = 200 and responseCode = 000
77. Validate Response 1. HTTP code = 200 and responseCode = 000 2. Check RTA Status
78. Validate Response Filter Role = ‘IDP’ only
79. Validate Response Http code = 202 and RequestId has value
80. Validate Response Http code = 202
81. Validate Response 1. Http code = 202 2. Check ndid_status and cust_action
82. Validate Response 1. Http code = 202 2. Retrieve customer_biometric
83. Validate Response FaceCompare result
84. Validate Response RMNo. Has value or not

### Page 13: Backup

1. Related Hosts 1. RM 2.SmartCard 3. DOPA-Gateway 4. CH24 5. SMS Gateway 6. PWS 7. BLDG-NDID 8. FARA 9. SAS 10. ST 11. DGEN
2. Sequence Diagram - NTB Registration
3. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
4. 0A. First Page (No Digital ID)
5. 1. Welcome Page
6. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
7. Ask Permission for - Activity tracking - Push notification
8. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, TandCUrl
9. Submit device meta data Request: metadata, location, message Response: T&C URL
10. 2. Accept T&C
11. System Token issued by PING
12. Auth_ID token (10minutes expired)
13. Auth ID token – return in every call, change to the new one every call (60 minutes expired)
14. Auth ID token in the request
15. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
16. CIS_Wrapper (1): Customer Search by Citizen ID Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
17. 3. Input CitizenID, DoB & Mobile
18. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
19. Check sum and format of Citizen ID
20. Private API - Group System token issued by Ping
21. StartProcessByCID Request: citizen ID, DOB, idType, MobileNo Response: citizen ID, DOB, prompt laserCode
22. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
23. If CIS profile not found or CIS status is invalid, search RM
24. CIAM logic to separate flows Has CIS -> Reactivate No CIS, Has RM -> ETB No CIS, No RM -> NTB
25. [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number to use for validation in screen 7 of NTB Flow and return response.
26. 4. Accept PDPA Consent
27. FARA (OCR Server)
28. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
29. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
30. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPAFULL}/asset-type/{assetType=JSON} Response: blobData, mimeType, version
31. Save Customer PDPA Acceptance (AcceptanceFlag, ConsentDate, ConsentTypeValue)
32. 5. NTB Step
33. [CIAM Validate] 1. Detection Score >= 0.6 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
34. IAM_22 (new): Submit data to OCR Request: image base 64 binary Response: Detection Score, ID Number, Thai Birth Date, Thai Title, Thai First Name, Thai Last Name, expiryDate, issuerDate, gender, EN Title, EN First Name, EN Last Name, DOB
35. Resolution 800 pixels
36. 6. Scan ID Card
37. Submit OCR Request: image base 64 binary Response: English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date *Remark Return value for Thai Title, English Title, Thai First Name, Thai Last Name, ID Number only
38. Prefill data from OCR 1. TitleNameTH / TitleNameEN 2. TH First name 3. TH Last name 4. CID (not editable)
39. ValidateLaserCode Request: idNum, LaserCodePID, Name, SurName, DOB, Response: prompt mobile number
40. IAM_05: Check DOPA (5 Fields) Request: PID, Name, SurName, DOB, LaserCode Response: ClientTransRef, ResponseCode, ResponseMesg
41. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
42. Validate 1. ID Expiry date >= Today 2. ID Issue Date <= Today
43. 7. Verify ID Card
44. Title name List hard code at frontend
45. [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
46. Save DOPADateTime
47. [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
48. IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
49. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
50. [CIAM Validate] CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
51. 8.1 Input Mobile No.
52. Validate 1. Mobile No. start with 06, 07, 08, 09 2. Mobile No. must have number 10 digits
53. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
54. SendSMSOTP Request: mobileNumber Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
55. IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
56. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: prompt PIN
57. [CIAM Validate] If OTP matches, then can proceed futher
58. 8.2 Verify Mobile No. By OTP
59. IAM_23 (new): Create OPO profile Request: idNum, idType, Title Name Thai, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, ID Expiry Date, ID Issue Date, TnCType, TnCAcceptDateTime, TnCVersion, TnCHash, PDPAFlag, PDPAPurposrCode, PDPAConsentDateTime, MobileNumber,DOPADateTime Response: ProcessInstantKey
60. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, ProcessInstantKey
61. #Cache PII data from CIAM
62. 9.1 Setup PIN
63. 9.2 Confirm PIN
64. Start Flow: Create Customer Temp Profile
65. Validate 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
66. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
67. If OPO returns error, end the flow.
68. Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
69. Validate 1. PIN and Confirm PIN is match
70. Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
71. Access Token AuthLevel = 3 CISId = Null ProcessInstantKey idenityStatus = preRegistration
72. Store Digital ID & DeviceBindingKey
73. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
74. Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
75. 10A.2 RTA-BeMyId Status Detail
76. 10A.1 Display Reference Code
77. 10. Select Authentication option
78. ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
79. ‘Processing’, ‘Register’ RTAStatus = ‘Processing’ or ‘Register’
80. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
81. ‘Locked’ RTAStatus = ‘Locked’
82. 10N.2
83. 10N.1
84. Get Latest RTA Record by CI and ProcessInstantKey
85. Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
86. If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
87. Please Continue sheet ‘RTA_BeMyID’ at Step then Back to Next step Mapping FlowType
88. OPO call delete Digital ID in user device and Direct customer to Beginning point
89. Logo Image should be get from Sitecore
90. If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
91. Image should be get from Sitecore
92. Please Continue sheet ‘RTA_NDID’ at Step then Back to Next step Mapping FlowType
93. In case have no RTA Record match by CI and ProcessInstantKey Then Get All RTA List from OPO DB by CI
94. Example IDP Error code with Warning Message
95. Screen Display depends on FlowType Validation
96. Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
97. 10B.4 RTA-NDID Status Detail
98. 10B.3 Pending Authen
99. ‘Error’ (RTAStatus = ‘ERROR’)
100. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
101. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
102. ‘Processing’ RTAStatus = ‘Processing’
103. Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
104. Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
105. OPO call delete Digital ID in user device and Direct customer to Beginning point
106. User Action : Select Authentication Option from [10D.1], [10D.2]
107. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
108. Please Refer to sheet ‘RTA_NDID’ or ‘RTA_BeMyID’ depends on customer selection
109. #Save State 2 - DigitalID - AuthLevel = -1 - ProcessInstantKey - State = 2
110. Validate All Lookup data has values Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
111. Get KYC Lookup Data (Fetch Task with Data return) Request: ProcessInstantKey Response: Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
112. Customer Tap ‘Next’
113. Common Service : Lookup Data
114. Get Customer Profile from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: idNum, Thai Title Name, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, Nationality, CountryOfResidence, PlaceOfBirth, MobileNumber,ContactNumber, OfficePhoneNumber, IDAddress, MaillingAddress, OfficeAddress, Education, Occupation, TypeOfBusiness, Position, OfficeName, SourceOfAsset, SourceOfFund, IncomePermonth, AssetValue, EarningCountry1-3 Remark: To get previous input in Customer KYC Section
115. 11. Input KYC Information
116. 11.1 Personal Detail
117. 11.2 Contact Information
118. 11.3 Education & Employment
119. 11.4 Income & Assets
120. 11.5 KYC Summary
121. If Customer Search Address
122. Common Service : Lookup Address
123. If Customer Search Country for Earning Country
124. Common Service : Lookup Country
125. Save information from Customer input to OPO DB (Temp)
126. Save KYC Information (Fetch Task) Request: ProcessInstantKey, KYC Information (each page) Response:
127. If Customer Tap ‘Next’ at Each page
128. If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
129. If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
130. Start Flow : Header: X-Language, X-Channel, Access Token Response: Selfie Face callback
131. If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
132. Check Profile at Ping - No CIS ID - Validate Auth level = 3 - idenityStatus = preRegistration
133. Get CustomerProfile Temp from OPO (Instead of CIS) Request:ProcessInstantKey Response:ID, IDType, IDExpiryDate, Nationality(For Foriegner in the future), AuthenticationMethod, ReferenceId
134. IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
135. Face Comparison Request: selfieImage Response: Status
136. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
137. 12.1 Intro before Face Scan
138. Get IDPImage-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, ImageBase64
139. If AuthenticationMode = ‘NDID’
140. Ask for camera permission
141. Liveness checking Capture selfie image
142. 12.2 Take a Selfie Photo for Face Scan
143. N E C
144. IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
145. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
146. CIAM checks bblscore. If it equals to 3, then can proceed further
147. 12.3 Face Scan Processing
148. If fail
149. If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
150. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
151. Onboard Customer Request: ProcessInstantKey, requestId Response: CISID Remark:
152. If pass face compare
153. Get Customer Profile Temp from OPO DB Objective: To Get CitizenId for CustomerSearch and Customer Profile Info for Create Profile
154. IAM_25 (new): Onboard Customer Header: ProcessInstantKey Request: requestId Response: cisId
155. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
156. Customer Search by Citizen ID Request: idNum Response: RMNo, CitizenId, RMNo
157. CIS_Wrapper (1): Customer Search by Citizen ID Request: idNum, {customerSearch} Response: RMNo, CitizenId, DoB
158. Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
159. CIS_Wrapper (2) : Get Customer Profile by RM No Request: RMNO, {customerProfile, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, customerProfileEdd, contactNumber, identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
160. If RMNo. Has value
161. Get Customer Profile by RMNo Request: RMNo. Response: All response fields from CIS
162. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
163. Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
164. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
165. Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
166. Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
167. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
168. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
169. Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
170. If: No RM Profile (Create CISID, Create RMNO)
171. - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
172. Validate Response No CIS, No RM -> Call Next Process H14:Create Customer Profile at RM No CIS, Has RM -> Call Next Process H15:Update Customer KYC at RM
173. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
174. If: Has RM Profile (Create CISID, Update RM Profile)
175. - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
176. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
177. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
178. Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
179. Access Token AuthLevel = 3 CIS ID ProcessInstantKey = Null idenityStatus = active
180. Update DigitalID Profile with 1. CIS ID 2. ProcessInstantKey= Null
181. Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
182. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
183. Exchange Token Request: ssoToken Response: AccessToken
184. E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
185. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
186. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
187. If API update CustomerProfileRelAdd fail
188. E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
189. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
190. Check if duplicate mobile no. in CIS Profile
191. If found duplicate mobile no.
192. Delete duplicate mobile no.
193. E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
194. [QA] CIS will update to KAFKA then IAM subscribe for recheck flag hasMobile No.
195. E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
196. H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
197. EOD Process (Existing) File - Batch Update RM profile (RM no., Phone number) File - Batch update relationship (RM No., CIS No.)
198. TSP
199. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: If Fail to Create TSP Profile, OPO will not retry
200. #Save State 3 - DigitalID - AuthLevel = 3 - State = 3
201. 13. Intro page to start apply product
202. Get Product Eligible [NEW] Request: CISID Response: ProductList {ProductId, ProductType, ProductNamtTH, ProductNameEN}
203. CIS_Wrapper (2) : Get Customer Profile by CIS ID Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
204. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
205. Get Product Eligible Request: IDType, CTCode, DOB, BBLIAL, IDPIAL, RiskLevel Response: ProductList{ProductId, ProductType, ProductNamtTH, ProductNameEN}
206. CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
207. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
208. 14. Eligible Product list
209. Please Refer to Open eSaving Sequence Diagram at Step ‘Get Product Detail’
210. Note Mapping Request Type for Face Compare
211. 10B.4 NDID RTA status ‘Approved’
212. 10A.2 BeMyID RTA status ‘Verified’
213. CIS_Wrapper (3): Create Customer Profile-NTB Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileIdentifications, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, contactNumber, email, agreement, consent, pdpa, channel, classification} Action: "CREATE_CUSTOMER_PROFILE" Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
214. CIS_Wrapper(3): Create Customer Profile-NTB (No CISID, has RMNO) Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, profile, contactNumber, agreement, identity, identifier, channel, classification, pdpa, consent, email} Action: CREATE_CUSTOMER_NTB_WITH_RM Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
215. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ channelTypeValue is not ‘na’ then continue to call H3: CustomerToAcctRel Inquiry - Else, Return Error
216. Logo IDP Bank App *Not Existing* Need to Place Image on Sitecore for New category and has configuration to get these logoes
217. Display Refence Code with ReferenceId last 7 digits in UpperCase format
218. B_CheckRTA #SubFlow
219. B_CheckRTA
220. M_CheckRTA
221. Set Save State = 1, Expiry date = 7 days
222. N_CheckRTA #SubFlow
223. B_Re-Gen RefNo
224. M_Re-Gen RTA
225. B_Cancel RTA
226. M_Cancel RTA
227. Liveness Check If Yes, do face compare
228. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version

### Page 14: NTB_Registration (MMP Backup)

1. Related Hosts 1. RM 2.SmartCard 3. DOPA-Gateway 4. CH24 5. SMS Gateway 6. PWS 7. BLDG-NDID 8. FARA 9. SAS 10. ST 11. DGEN
2. Sequence Diagram - NTB Registration
3. 1 First Page (No Digital ID)
4. Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
5. 2. Welcome Page
6. TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
7. Start Flow Header: X-Language, X-Channel Response: device profile collector callback
8. Ask Permission for - Activity tracking - Push notification
9. Cache allowPushFlag
10. Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
11. [ActivityLog] Step 2 - Customer Enrollment Welcome Page - Response 1 - Responds back with a DeviceProfileCallback - Response 2 - Case: Customer device is not locked - End flow - Customized error - End flow - OOTB error
12. Submit device meta data Request: metadata, location, message Response: T&C URL
13. IAM_01: T&C content Inquiry Request: language (according to x-language) Response: version, TandCUrl
14. 3. Accept T&C
15. System Token issued by PING
16. Auth_ID token (10minutes expired)
17. After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
18. Auth ID token – return in every call, change to the new one every call (60 minutes expired)
19. [AuditLog] IAM Proxy sheet - IAM_01 Response
20. Auth ID token in the request
21. CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
22. [ActivityLog] Step 3 - Customer Enrollment T&C - Response 3 - responds back with CND - End flow - OOTB error
23. 4. Input CitizenID, DoB & Mobile
24. Check sum and format of Citizen ID
25. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
26. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC) CBS off host - 2:30-3:00am (avg): Error at this point
27. Private API - Group System token issued by Ping
28. IAM_02: Customer Search Request: idNum Response: cisId, cisIdStatus, channel, rmNum, dob
29. StartProcessByCID Request: citizen ID, DOB, idType Response: citizen ID, DOB, prompt laserCode
30. If CIS profile not found or CIS status is invalid, search RM
31. CIAM logic to separate flows Has CIS -> Reactivate No CIS, Has RM -> ETB No CIS, No RM -> NTB
32. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
33. [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
34. [AuditLog] IAM Proxy sheet - IAM_02 Response
35. [AuditLog] Step 4 - Customer Enrollment Citizen ID, DOB and Mobile Number - Response 4 - Response NTB - Response 4 - go back to T&C - End flow - Customized error - End flow - OOTB error
36. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=PDPAFULL}/asset-type/{assetType=JSON} Response: blobData, mimeType, version
37. 5. Accept PDPA Consent
38. IAM_10: Get PDPA content Request: language Response: version, pdpacontentUrl
39. [ActivityLog] Step 4 - NTB - Citizen ID and DOB Continued - Response 4.1 - Response with PDPA - End flow - Customized error - End flow - OOTB error
40. [AuditLog] IAM Proxy sheet - IAM_10 Response
41. Save Customer PDPA Acceptance (AcceptanceFlag, ConsentDate, ConsentTypeValue)
42. 6. NTB Step
43. [ActivityLog] Step 5 - NTB Onboarding - Full PDPA Consent - Response 5.1 - Response with OCR - End flow - OOTB error
44. FARA (OCR Server)
45. Resolution 800 pixels
46. 7. Scan ID Card
47. Submit OCR Request: image base 64 binary Response: English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date *Remark Return value for Thai Title, English Title, Thai First Name, Thai Last Name, ID Number only
48. H2: Submit ID Card Image to OCR POST: {{OCRHostURL}}/idocr/detect/front Header: Content-Type “multipart/form-data” Request: ID Card image base64 string convert to binary Response: Address Line 1, Address Line 2, English Birth Date, English Expiry Date, English Title, English First Name, English Last Name, English Issue Date, ID Number, ID Card Image, Message From OCR Server, Process Time, Religion, Thai Birth Date, Thai Expiry Date, Thai Title, Thai First Name, Thai Last Name, Thai Issue Date, Detection Score
49. IAM_22 (new): Submit data to OCR Request: image base 64 binary Response: Detection Score, ID Number, Thai Birth Date, Thai Title, Thai First Name, Thai Last Name, expiryDate, issuerDate, gender, EN Title, EN First Name, EN Last Name, DOB
50. [AuditLog] IAM Proxy sheet - IAM_22 Response
51. [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
52. [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
53. Prefill data from OCR 1. TitleNameTH / TitleNameEN 2. TH First name 3. TH Last name 4. CID (not editable)
54. ValidateLaserCode Request: idNum, LaserCodePID, Name, SurName, DOB, Response: prompt mobile number
55. IAM_05: Check DOPA (5 Fields) Request: PID, Name, SurName, DOB, LaserCode Response: ClientTransRef, ResponseCode, ResponseMesg
56. H3: DOPA_CheckCardService - Check Card By Laser (5 fields) Request: CitizenID, firstName, lastName, DoB, Laser Code Response: code, description
57. Validate 1. ID Expiry date >= Today 2. ID Issue Date <= Today
58. 8. Verify ID Card
59. Title name List hard code at frontend
60. [AuditLog] IAM Proxy sheet - IAM_05 Response
61. [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
62. [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
63. IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
64. Save DOPADateTime
65. [CIAM Validate] CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
66. [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
67. H4: CustomerSuspiciousAcctInq POST:/esis/customer-services/customers/suspicious/inquiry Request: CitizenID Response: idNum, resultCode, resultDesc
68. [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
69. H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
70. Validate 1. Mobile No. start with 06, 07, 08, 09 2. Mobile No. must have number 10 digits
71. SendSMSOTP Request: mobileNumber (in IA cache) Response: OTP, smsRef, otpResendsRemaining, otpRetriesRemaining
72. IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
73. [AuditLog] IAM Proxy sheet - IAM_08 Response
74. 9. Verify Mobile No. By OTP
75. VerifyMobileNumberWithOTP Request: OTP, smsRef Response: prompt PIN
76. [CIAM Validate] If OTP matches, then can proceed futher
77. [ActivityLog] Step 8 - NTB Onboarding - Verify Mobile using OTP - Response 8.1 - Response with PIN - Response - 8.2 - Resend OTP - In flow error Response 8.3.1 - OTP is incorrect (1 attempt) - In flow error Response 8.3.2 - OTP is incorrect (2 attempt) - In flow error Response 8.3.3 - OTP is expired - End flow - Customized error - End flow - OOTB error
78. IAM_23 (new): Create OPO profile Request: idNum, idType, Title Name Thai, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, ID Expiry Date, ID Issue Date, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion,TnCHash, PDPAFlag, PDPAPurposrCode, PDPAConsentDateTime, MobileNumber, DOPADateTime Response: ProcessInstantKey
79. SetupPIN Request: PIN Response: Access Token, Refresh Token, ID Token, DeviceFingerprintID, ProcessInstantKey
80. #Cache PII data from CIAM
81. 10.1 Setup PIN
82. 10.2 Confirm PIN
83. Start Flow: Create Customer Temp Profile
84. Validate 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
85. [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
86. If OPO returns error, end the flow.
87. Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
88. Validate 1. PIN and Confirm PIN is match
89. Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
90. Access Token AuthLevel = 3 CISId = Null ProcessInstantKey idenityStatus = preRegistration
91. Store Digital ID & DeviceBindingKey
92. [AuditLog] (Fail Only) Step 1 – NTB Registration – Create Customer Profile Temp
93. [AuditLog] Step 9 - NTB Onboarding - Register PIN - Response 9 - Enroll the customer’s device - End flow - Customized error - End flow - OOTB error
94. [AuditLog] Step 10 - NTB Onboarding - Bind Device - Response 10 - end of the onboarding process save state 1 - End flow - Customized error - End flow - OOTB error
95. [AuditLog] IAM Proxy sheet - IAM_23 Response
96. #Save point: Save State 1 - DigitalID - AuthLevel = 3 - ProcessInsantKey - State = 1
97. Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
98. 11A.2 RTA-BeMyId Status Detail
99. 11A.1 Display Reference Code
100. 11. Select Authentication option
101. ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
102. ‘Processing’, ‘Register’ RTAStatus = ‘Processing’ or ‘Register’
103. ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
104. ‘Locked’ RTAStatus = ‘Locked’
105. 11N.2
106. 11N.1
107. Get Latest RTA Record by CI and ProcessInstantKey
108. Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
109. If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
110. Please Continue sheet ‘RTA_BeMyID’ at Step then Back to Next step Mapping FlowType
111. OPO call delete Digital ID in user device and Direct customer to Beginning point
112. Logo Image should be get from Sitecore
113. If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
114. Image should be get from Sitecore
115. Please Continue sheet ‘RTA_NDID’ at Step then Back to Next step Mapping FlowType
116. In case have no RTA Record match by CI and ProcessInstantKey Then Get All RTA List from OPO DB by CI
117. Example IDP Error code with Warning Message
118. Screen Display depends on FlowType Validation
119. Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
120. 11B.4 RTA-NDID Status Detail
121. 11B.3 Pending Authen
122. ‘Error’ (RTAStatus = ‘ERROR’)
123. ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
124. ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
125. ‘Processing’ RTAStatus = ‘Processing’
126. Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
127. Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
128. OPO call delete Digital ID in user device and Direct customer to Beginning point
129. User Action : Select Authentication Option from [10D.1], [10D.2]
130. Display WarningMessage depends mapping of IDP error Code returned (Need to store mapping of IDP error code and WarningMessageTH, WarningMessageEn)
131. Please Refer to sheet ‘RTA_NDID’ or ‘RTA_BeMyID’ depends on customer selection
132. #Save State 2 - DigitalID - AuthLevel = -1 - ProcessInstantKey - State = 2
133. Validate All Lookup data has values Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
134. Get KYC Lookup Data (Fetch Task with Data return) Request: ProcessInstantKey Response: Country, Province, Amphua, Tambon, Postal, MaritalStatus, EarningCountry, SourceOfFund, SourceOfAsset, AssetValue, IncomePer Month, TypeOfBusiness, Education, Occupation
135. Customer Tap ‘Next’
136. Common Service : Lookup Data
137. Get Customer Profile from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: idNum, Thai Title Name, Thai First Name, Thai Last Name, English Title Name, English First Name, English Last Name, Date of Birth, Nationality, CountryOfResidence, PlaceOfBirth, MobileNumber,ContactNumber, OfficePhoneNumber, IDAddress, MaillingAddress, OfficeAddress, Education, Occupation, TypeOfBusiness, Position, OfficeName, SourceOfAsset, SourceOfFund, IncomePermonth, AssetValue, EarningCountry1-3 Remark: To get previous input in Customer KYC Section
138. 12. Input KYC Information
139. 12.1 Personal Detail
140. 12.2 Contact Information
141. 12.3 Education & Employment
142. 12.4 Income & Assets
143. 12.5 KYC Summary
144. If Customer Search Address
145. Common Service : Lookup Address
146. If Customer Search Country for Earning Country
147. Common Service : Lookup Country
148. Save information from Customer input to OPO DB (Temp)
149. Save KYC Information (Fetch Task) Request: ProcessInstantKey, KYC Information (each page) Response:
150. If Customer Tap ‘Next’ at Each page
151. If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
152. If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
153. [ActivityLog] (Sucess/Fail) Step 18 - NTB Registration – Save KYC Info
154. If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
155. Start Flow : Header: X-Language, X-Channel, Access Token Response: Selfie Face callback
156. Check Profile at Ping - No CIS ID - Validate Auth level = 3 - idenityStatus = preRegistration
157. [ActivityLog] Step 1 - NTB Onboarding Face Verification – Initiate - Response 1 - Response with Facial Verification - End flow - Customized error - End flow - OOTB error
158. Get CustomerProfile Temp from OPO (Instead of CIS) Request:ProcessInstantKey Response:ID, IDType, IDExpiryDate, Nationality(For Foriegner in the future), AuthenticationMethod, ReferenceId
159. IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
160. Face Comparison Request: selfieImage Response: Status
161. H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
162. 13.1 Intro before Face Scan
163. Get IDPImage-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, ImageBase64
164. If AuthenticationMode = ‘NDID’
165. Ask for camera permission
166. Liveness checking Capture selfie image
167. [AuditLog] IAM Proxy sheet - IAM_24 Response
168. 13.2 Take a Selfie Photo for Face Scan
169. N E C
170. IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
171. H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
172. CIAM checks bblscore. If it equals to 3, then can proceed further
173. 13.3 Face Scan Processing
174. If fail
175. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
176. If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
177. Onboard Customer Request: ProcessInstantKey, requestId Response: CISID Remark:
178. Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
179. If pass face compare
180. Get Customer Profile Temp from OPO DB Objective: To Get CitizenId for CustomerSearch and Customer Profile Info for Create Profile
181. IAM_25 (new): Onboard Customer Header: ProcessInstantKey Request: requestId Response: cisId
182. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
183. CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: RMNo, CitizenId, DoB
184. Customer Search by Citizen ID Request: idNum Response: RMNo, CitizenId, RMNo
185. [AuditLog] (Fail Only) Step 19 - NTB Registration – Customer Search RM
186. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
187. Validate Response If RMNo has value, then Continue to Call Get Customer Profile by ID Number. Else if RMNo has no value, then skip Get Customer Profile by ID Number and Continue to Call H13: CustomerRiskService-AMLRiskRating
188. CIS_Wrapper() (new): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, Segment, BAN
189. If RMNo. Has value
190. CH24
191. Get Customer Profile by ID Number Request: idNum Response: All response fields from CIS
192. (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, Segment, BAN
193. [AuditLog] (Fail Only) Step 20 - NTB Registration – Get Customer Profile Remark: mask BAN
194. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/customer-profile/v2/internal/customers/inquiry", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
195. Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
196. H13: CustomerRiskService-AMLRiskRatingInq POST: /esis/customer-risk-services/customer/aml/risk-rating/check Request: RM Number, Product Code, Thai Fullname, English Fullname, ID Type, ID Number, DOB, Gender, Customer Type, CT Code, ID Address, Office Address, Mailing Address, Nationality, Country of residence, Occupation, Earning of country1-3, Type of business, First Account Date, Existing Risk Level, Existing Risk Reason Code, Good Guy Flag Response: Highest Risk Rating, Highest Risk Filtering
197. [AuditLog] (Fail Only) Step 21 - NTB Registration – Check AML Risk Rating
198. Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
199. Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
200. Set segmentLevel = A13 for default segment of “Create Customer Profile-NTB”
201. Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
202. H1: Customer search POST:/esis/customer-services/customers/search Request: CitizenID Response: CitizenID, DoB, RM No. มีโอกาส Response มากกว่า 1 record -> เลือกใช้ RM อันนึง (assume first RM no. – TBC)
203. If: No RM Profile (Create CISID, Create RMNO)
204. - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
205. H14: Create Customer Profile at RM POST: Request: SubmitDate, CondUpdateCustFlag, RMCustNum, NameLine, EnglishName, NameType, IDType, IDNum, IssueDate, ExpiryDate, BirthDate, CustType, GenderCode, AddressType(MAIL , IDADDR , OFFICE), AddressNum(MAILAddress, IDAddress, OfficeAddress), Street(MAILAddress, IDAddress, OfficeAddress), SubDistrict(MAILAddress, IDAddress, OfficeAddress), District(MAILAddress, IDAddress, OfficeAddress), State(MAILAddress, IDAddress, OfficeAddress), PostalCode(MAILAddress, IDAddress, OfficeAddress), ISOCountryCode(MAILAddress, IDAddress, OfficeAddress), TelephoneNum, TelephoneType, TelephoneExtension, EmailAddress,Nationality[0] ,CountryOfResidence ,MaritalStatus ,OccupationCode ,IncomePerMonth ,FaceToFaceFlag , BBLIALCode, BBLIALLastMaintenanceDate, BBLTellerID, BBLChannelBranch, IDPIALCode, IDPIALAddedDate, IDPBankCode, IDPCustCreationFlag, EducationCode, OfficeName, Position, Nationality[1], Nationality[2], PlaceOfBirth,TaxReportCode, SubstantialPresentTestIndicator, GreenCardFlag, ClassificationCode, ForeignTaxIDTypeCode, ForeignTaxIDNum, ConsentFlag, ConsentProcessingBranch, RiskLevel, RiskLevelReasonCode, RiskLevelUpdateDate, RiskLevelUpdateBy, KYCStatus, KYCUpdateDate, KYCUpdateBy, SourceOfAsset, ValueOfAsset, EarningFromCountry, RiskOccupation Response: RMCustNum Note: Reference from ChannelService-OnboatdCustomerAdd without Account Profile in Request
206. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
207. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Create RMNO' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/echannel/profile", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
208. (NEW) H22: Update Segment Level ถ้า Fail ก็ Ignore แต่ยัง Update CIS เป็น A13 Request: RM No., Segment Level Response: Update datetime
209. If: Has RM Profile (Create CISID, Update RM Profile)
210. - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
211. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
212. [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
213. H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
214. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Update CustomerProfile' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/profiles/new-account-compliance", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
215. Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
216. (NEW) H22: Update Segment Level ถ้า Fail ก็ Ignore แต่ยัง Update CIS เป็น A13 Request: RM No., Segment Level Response: Update datetime
217. Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
218. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = <env>.raw.cis.party.create - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
219. Access Token AuthLevel = 3 CIS ID ProcessInstantKey = Null idenityStatus = active
220. Update DigitalID Profile with 1. CIS ID 2. ProcessInstantKey= Null
221. [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - Response 2 - end of the onboarding process save state 3 IAM Proxy sheet - IAM_25 Response
222. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
223. [AuditLog] (Fail Only) Step 22 - NTB Registration – Create CIS Profile
224. E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
225. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = <env>.raw.cis.party.create/ <env>.raw.cis.party.update - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
226. H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
227. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
228. H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
229. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
230. If API update CustomerProfileRelAdd fail
231. E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
232. Delete phone number from other profile (if duplicate) -> Broadcast to other systems
233. Check if duplicate mobile no. in CIS Profile
234. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = Map <Kafka topic name> - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
235. If found duplicate mobile no.
236. Delete duplicate mobile no.
237. E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
238. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = Map <Kafka topic name> - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
239. [QA] CIS will update to KAFKA then IAM subscribe for recheck flag hasMobile No.
240. E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
241. EOD Process (Existing) File - Batch Update RM profile (RM no., Phone number) File - Batch update relationship (RM No., CIS No.)
242. H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
243. [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = n/a - alternateIdType = n/a - alternateId = n/a - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = `Batch’ - actType = 'Batch from CIS' - actSubType = 'Batch Add Relationship to RM'/ 'Batch Update Mobile Number to RM' - actStatus = Batch file transfer result (Exit Code) - errorCode = batch_job_execution.exit_code - errorMessage = batch_job_execution.exit_message (first 200 char) - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = แต่ละ step ของ Batch
244. (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
245. oCRM
246. If get daily total limit from oCRM error, then set segmentLevel (from oCRM) is A13
247. Compare Segment & Daily Total Limit 1. Get daliyTotalLimit by segment (from RM) in configure D13 -> 30,000 2. Validate dailyTotalLimit If Max of dailyTotalLimit (from oCRM) >= dailyTotalLimit (from RM - H19), then set - segmentLevel = segmentLevel (from oCRM) D13, Otherwise, If get daily total limit from oCRM (H21) success, set - segmentLevel = 1st digit of segmentLevel (from oCRM) B + all digit exclude 1st digit of segmentLevel (from RM). Else, set segmentLevel = segmentLevel (from RM)
248. CIS_Wrapper() (new): Update Segment Level วิ่งไป RM ก่อน แล้วค่อย Update ตัวเอง POST: Request: CIS ID, Segment Level, BAN (optional) Response: -
249. Update Segment Level Request: CIS ID, Segment Level Response: All response fields from CIS
250. (NEW) H22: Update Segment Level Request: RM No., Segment Level Response: Update datetime
251. E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
252. TSP
253. OPO get EntraID (Virtual ID)
254. [ActivityLog] (Fail Only) Step 23 - NTB Registration – Update segment
255. TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Compare Segment & Daily Total Limit” For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
256. Remark: This is an independent process
257. [ActivityLog] (Sucess/Fail) Step 24 - NTB Registration – Create TSP Profile
258. Check isAllowPushNoti flag in cache align on setting in device
259. CNH
260. Get Pushed Token from FCM
261. If allowPushFlag is ‘Y’, Else skip process
262. #Save State 3 - DigitalID - AuthLevel = 3 - State = 3
263. 14. Intro page to start apply product
264. Get Product Eligible [NEW] Request: CISID Response: ProductList {ProductId, ProductType, ProductNamtTH, ProductNameEN}
265. [ActivityLog] (Sucess/Fail) Step 23 - NTB Registration – Create TSP Profile
266. CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
267. H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
268. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
269. [AuditLog] (Fail Only) Step 25 - NTB Registration – Get Customer Profile
270. Get Product Eligible Request: IDType, CTCode, DOB, BBLIAL, IDPIAL, RiskLevel Response: ProductList{ProductId, ProductType, ProductNamtTH, ProductNameEN}
271. CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
272. 15. Eligible Product list
273. H19: CustomerToAcctRel Inquiry POST:/esis/channel-services/customers/accounts/relationship/inquiry Request: RM, Account Types (AppID), nextKey Response: accountControlCode, appId, accountNum,relationshipCode, ownershipCode, accountProdCode, accountType, accountTypeDescription, accountStatus, currencyCode, numberOfAccountOwners, nextKey
274. [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
275. [AuditLog] (Fail Only) Step 26 - NTB Registration – Get RM Account List
276. Please Refer to Open eSaving Sequence Diagram at Step ‘Get Product Detail’
277. Note Mapping Request Type for Face Compare
278. 11B.4 NDID RTA status ‘Approved’
279. 11A.2 BeMyID RTA status ‘Verified’
280. CIS_Wrapper (3): Create Customer Profile-NTB POST: /customerprofile/api/v2/cis/internal/customers/new Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileIdentifications, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, contactNumber, email, agreement, consent, pdpa, channel, classification} Action: "CREATE_CUSTOMER_PROFILE" Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
281. CIS_Wrapper(3): Create Customer Profile-NTB (No CISID, has RMNO) Request: {customerProfile *Add New field ‘Registration Channel’, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, party, profile, contactNumber, agreement, identity, identifier, channel, classification, pdpa, consent, email} Action: CREATE_CUSTOMER_NTB_WITH_RM Response: CIS ID, RMNO, EXTID, classificationType, classificationTypeValue, prefix, firstName, midName, lastName Remark: Possible Values for Registration Channel could be - ‘NTB-NDID’ - ‘NTB-BeMyId’
282. [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
283. Logo IDP Bank App *Not Existing* Need to Place Image on Sitecore for New category and has configuration to get these logoes
284. Display Refence Code with ReferenceId last 7 digits in UpperCase format
285. Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
286. B_CheckRTA #SubFlow
287. B_CheckRTA
288. M_CheckRTA
289. Set Save State = 1, Expiry date = 7 days
290. Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
291. N_CheckRTA #SubFlow
292. B_Re-Gen RefNo
293. M_Re-Gen RTA
294. B_Cancel RTA
295. M_Cancel RTA
296. Liveness Check If Yes, do face compare
297. CMS_01: /cms/consent/v1/document/product-type/{productTypeCode=NEWAPP}/doc-type/{docTypeCode4=TNC}/asset-type/{assetType=HTML} Response: blobData, mimeType, version

## Optional Branches

- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- If CIS profile not found or CIS status is invalid, search RM
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- [CIAM Validate] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B", the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B", the customer will be treated as non-suspicious.
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- 11. Select Authentication option
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’ and ExpiryDateTime > DateTime.Now] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- User Action : Select Authentication Option from [10D.1], [10D.2]
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If AuthenticationMode = ‘NDID’
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
- If RMNo. Has value
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- Retry 3 times
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Liveness Check If Yes, do face compare
- 10. Select Authentication option
- Validate RTA Record If [RTAStatus = ‘Register’ or ‘Processing’] then,Return General Error Else, proceed next step to call Generate CustomerRefNo
- Validate Response If (H6) HTTP response code = 200 and responseCode = 000 Then, Insert DB with ReferenceId, IdNum, ProcessInstantKey, RTAId, RTACreateDateTime, RTAStatus = (status), RTAExpiryDateTime = (RTACreateDateTime+Duration Of Timeout)
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to next step H6: GenerateRTA-BeMyID Else if RTAStatus = ‘Locked’ or ‘Expired’ or ‘Rejected’ Then Skip H6 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- If Customer Action: Tap ‘I’ve Enter My code’
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate RTAStatus If RTAStatus = ‘Register’ and ExpiryDateTime > DateTime.Now or RTAStatus = ‘Processing’ then, proceed next step to call (H7): InquiryRTA-BeMyID
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H7 as below: If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If ID Number is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If Issue Date is match then Set IssueDate_PassValidateFlag = ‘Y’ Else IssueDate_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- 10. Select Authentication option
- Validate IDP List If IDP has Preferred IDP Flag = ‘Y’ Then display IDP in section ‘Enrolled’ Elese, display in Section ‘Not Enrolled’
- 1. Get RTA List from OPO DB by CI If Count of ReferendId start with ‘NCBD_XXX’ >= 10 then, return Error Else continue Next to Get Latest RTA 2. Get Latest RTA Record by CI and ProcessInstantKey If RTAStatus = ‘Processing’ Then, Return General Error Else, proceed next step to call Generate ReferenceId
- H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- Navigate to 10. Select Authentication option
- Validate Response If (H9) HTTP response code = 202 and RequestId has value Then, Insert DB with ReferenceId, RequestId, IDNum, ProcessInstantKey, UpdateDateTime, RTAStatus = ‘Processing’, RTACreateDateTime, CompanyCode, IndustryCode, appNameTh, appNameEn
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
- Validate Response If (H9) HTTP response code = 202 Update DB with UpdateDateTime, RTAStatus = ‘Cancelled’
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- If Customer Action: Tap ‘I’ve already authenticated’
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed next step to call (H10): Get RTA Status-NDID
- Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
- Validate RTA Expiry If Not Expired then, Proceed further Else, Update DB with UpdateDateTime, RTAStatus = ‘Expired’
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H10 as below: #To Be Revise If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If English First Name is match then Set FirstNameEN_PassValidateFlag = ‘Y’ Else FirstNameEN_PassValidateFlag = ‘N’ If English Last Name is match then Set LastNameEN_PassValidateFlag = ‘Y’ Else LastNameEN_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If ID is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 4, if not, returns in-flow error (users can retry)
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
- [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
- [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
- 11. Select Authentication option
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- User Action : Select Authentication Option from [10D.1], [10D.2]
- [ActivityLog] Step 15 - NTB Registration – Get Customer Information Response2: Fail (Log Level1)
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
- [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
- [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
- If AuthenticationMode = ‘NDID’
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
- [AuditLog] in case Fail/Success Only API Inquiry without JWT token
- Validate Response If status.code is “2005”, refer case “RMNo Has no Value” Otherwise, refer case “RMNo Has Value”
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
- Validate Response If RiskRating < 3, Then update Risk Level, Risk Reason Code into (Customer Profile Temp of OPO DB) proceed next step to Save State Expiry. Else, return error
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If identityVerifiedChannel = 002 beMyId
- [AuditLog] in case Fail/Success Only CIS RM Update IAL
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- [AuditLog] in case Fail/Success Only API CREATE ACTION:
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
- [AuditLog] in case Fail/Success Only Backend API Update PDPA
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- Prepare data for Call “H21: Get Daily Total Limit”. Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 4. RM Number Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now 2. RM Number from Response of “Create Customer Profile-NTB”
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
- [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. settingsDetails/transactionLimitScheme​ = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”“05”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- If Update Segment Level failed,
- [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
- Retry 3 times
- [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
- [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
- Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
- If Fail, then make pendingRegisterFlag is true
- [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Liveness Check If Yes, do face compare
- POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3 - Add DWR Device profiling at beginning of onboarding and before request EFM to approval Remark: Since DWN charging model so decided to add at Entry - Add API call to EFM for request to approve - [#TBC] EFM Advice message via KAFKA
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NTB :transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘IDCard’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 4, if not, returns in-flow error (users can retry)
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] If OTP matches, then can proceed futher
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPIN’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
- [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
- [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
- [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
- 11. Select Authentication option
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- User Action : Select Authentication Option from [10D.1], [10D.2]
- [ActivityLog] Step 15 - NTB Registration – Get Customer Information Response2: Fail (Log Level1)
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
- [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
- [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
- If AuthenticationMode = ‘NDID’
- CIAM checks bblscore. If it equals to 3, then can proceed further
- POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
- [AuditLog] in case Fail/Success Only API Inquiry without JWT token
- Validate Response If status.code is “2005”, refer case “RMNo Has no Value” Otherwise, refer case “RMNo Has Value”
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
- Validate Response If RiskRating < 3, Then update Risk Level, Risk Reason Code into (Customer Profile Temp of OPO DB) proceed next step to Save State Expiry. Else, return error
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If identityVerifiedChannel = 002 beMyId
- [AuditLog] in case Fail/Success Only CIS RM Update IAL
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- [AuditLog] in case Fail/Success Only API CREATE ACTION:
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’: transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
- [AuditLog] in case Fail/Success Only Backend API Update PDPA
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- Prepare data for Call “H21: Get Daily Total Limit”. Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 4. RM Number Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now 2. RM Number from Response of “Create Customer Profile-NTB”
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
- [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- If Update Segment Level failed,
- [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
- Retry 3 times
- [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
- [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
- If Fail, then make pendingRegisterFlag is true
- [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Liveness Check If Yes, do face compare
- If CIS profile not found or CIS status is invalid, search RM
- Authentication Option : BeMyID
- 10 Select Verify Option
- Authentication Option : NDID
- H9: GenerateRTA-NDID URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- If: No CIS ID, No RM Profile
- If: No CIS ID, Has RM Profile
- Prepare data for Call “H21: Get Daily Total Limit”. Fields from Response of “Create Customer Profile-NTB” 1. RM Number Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- 10. Select Authentication option
- Validate RTA Record If [RTAStatus = ‘Register’ or ‘Processing’] then,Return General Error Else, proceed next step to call Generate CustomerRefNo
- Validate Response If (H6) HTTP response code = 200 and responseCode = 000 Then, Insert DB with ReferenceId, IdNum, ProcessInstantKey, RTAId, RTACreateDateTime, RTAStatus = (status), RTAExpiryDateTime = (RTACreateDateTime+Duration Of Timeout)
- [AuditLog] Step 4 - NTB Registration - Create BeMyId RTA Response1: Success Response2: Fail
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to next step H6: GenerateRTA-BeMyID Else if RTAStatus = ‘Locked’ or ‘Expired’ or ‘Rejected’ Then Skip H6 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
- [AuditLog] Step 5 - NTB Registration – Cancel BeMyId RTA Response1: Success Response2: Fail
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- [ActivityLog] Step 5 - NTB Registration – Cancel BeMyId Request Response1: Success (Log level2) Response2: Fail (Log Level1)
- If Customer Action: Tap ‘I’ve Enter My code’
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate RTAStatus If RTAStatus = ‘Register’ or ‘Processing’ then, proceed next step to call (H7): InquiryRTA-BeMyID
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- [AuditLog] Step 6 - NTB Registration – Check BeMyId RTA Status Response1: Success Response2: Fail
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H7 as below: If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If ID Number is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If Issue Date is match then Set IssueDate_PassValidateFlag = ‘Y’ Else IssueDate_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- [ActivityLog] Step 7 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : Null NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_DipChip’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
- 10. Select Authentication option
- [AuditLog] Step 8 - NTB Registration – Get NDID TC Response1: Success Response2: Fail
- [AuditLog] Step 9 - NTB Registration – NDID TC Acceptance Response1: Success Response2: Fail
- Validate IDP List If IDP has Preferred IDP Flag = ‘Y’ Then display IDP in section ‘Enrolled’ Elese, display in Section ‘Not Enrolled’
- [AuditLog] Step 10 - NTB Registration – GetIDPBankList Response1: Success Response2: Fail
- 1. Get RTA List from OPO DB by CI If Count of ReferendId start with ‘NCBD_XXX’ >= 10 then, return Error Else continue Next to Get Latest RTA 2. Get Latest RTA Record by CI and ProcessInstantKey If RTAStatus = ‘Processing’ Then, Return General Error Else, proceed next step to call Generate ReferenceId
- H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- Navigate to 10. Select Authentication option
- Validate Response If (H9) HTTP response code = 202 and RequestId has value Then, Insert DB with ReferenceId, RequestId, IDNum, ProcessInstantKey, UpdateDateTime, RTAStatus = ‘Processing’, RTACreateDateTime, CompanyCode, IndustryCode, appNameTh, appNameEn
- [AuditLog] Step 11 - NTB Registration – Create NDID RTA Response1: Success Response2: Fail
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
- Validate Response If (H9) HTTP response code = 202 Update DB with UpdateDateTime, RTAStatus = ‘Cancelled’
- [AuditLog] Step 12 - NTB Registration – Cancel NDID RTA Response1: Success Response2: Fail
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- If Customer Action: Tap ‘I’ve already authenticated’
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed next step to call (H10): Get RTA Status-NDID
- [AuditLog] Step 13 - NTB Registration – Check NDID RTA Status Response1: Success Response2: Fail
- Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
- Validate RTA Expiry If Not Expired then, Proceed further Else, Update DB with UpdateDateTime, RTAStatus = ‘Expired’
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H10 as below: #To Be Revise If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If English First Name is match then Set FirstNameEN_PassValidateFlag = ‘Y’ Else FirstNameEN_PassValidateFlag = ‘N’ If English Last Name is match then Set LastNameEN_PassValidateFlag = ‘Y’ Else LastNameEN_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If ID is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- [ActivityLog] Step 14 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_NDID’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page Else if
- CIAM checks 1. Validate DPoP proof - validate auth 2. Access Token is valid or not 3. Channel status - Locked > PIN locked alert - Active > Go to next step 4. PIN is valid or not
- 1. Get Current Save State 2. Validate Save state Expiry à If Save state is not expired, Then Return currentState à Else if Save state is expired or could not find save state, then Return error ERR_OPO_COM_034
- Validate Response If currentState in state 1, then continue to call Get RTA List from OPO DB Else if currentState in state 2, then continue to call Get KYC Lookup Data
- If Save State = 1 then, direct customer to Get RTA List from OPO DB
- If Save State = 2 then, direct customer to KYC
- If Save State = 3 then, direct customer to product origination
- POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page Else if
- CIAM checks 1. Validate DPoP proof - validate auth 2. Access Token is valid or not 3. Channel status - Locked > PIN locked alert - Active > Go to next step 4. PIN is valid or not
- 1. Get Current Save State 2. Check CIS ID in customer prospect table à If CIS ID have value, return error ERR_OPO_NTB_043. à Otherwise, continue to proceed No.3 3. Validate Save state Expiry à If Save state is not expired, Then Return currentState à Else if Save state is expired or could not find save state, then Return error ERR_OPO_COM_034
- Validate Response If currentState in state 1, then continue to call Get RTA List from OPO DB Else if currentState in state 2, then continue to call Get KYC Lookup Data
- If Save State = 1 then, direct customer to Get RTA List from OPO DB
- If Save State = 2 then, direct customer to KYC
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- [AuditLog] in case Fail Only Step 7 - NTB Onboarding - Laser Code - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- [AuditLog] (Fail Only) Step 1 – NTB Registration – Create Customer Profile Temp
- 11. Select Authentication option
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- User Action : Select Authentication Option from [10D.1], [10D.2]
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] (Sucess/Fail) Step 18 - NTB Registration – Save KYC Info
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If AuthenticationMode = ‘NDID’
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- [AuditLog] (Fail Only) Step 19 - NTB Registration – Customer Search RM
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
- If RMNo. Has value
- [AuditLog] (Fail Only) Step 20 - NTB Registration – Get Customer Profile
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] (Fail Only) Step 21 - NTB Registration – Check AML Risk Rating
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Create RMNO' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/echannel/profile", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Update CustomerProfile' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/profiles/new-account-compliance", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] (Fail Only) Step 22 - NTB Registration – Create CIS Profile
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- Retry 3 times
- [ActivityLog] (Sucess/Fail) Step 23 - NTB Registration – Create TSP Profile
- If allowPushFlag is ‘Y’, Else skip process
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] (Fail Only) Step 24 - NTB Registration – Get Customer Profile
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Liveness Check If Yes, do face compare
- If CIS profile not found or CIS status is invalid, search RM
- Authentication Option : BeMyID
- 10 Select Verify Option
- Authentication Option : NDID
- H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- If RMNo. Has value
- If: No CIS ID, No RM Profile
- If: No CIS ID, Has RM Profile
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- If CIS profile not found or CIS status is invalid, search RM
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] 1. Detection Score >= 0.6 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- 10. Select Authentication option
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- User Action : Select Authentication Option from [10D.1], [10D.2]
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If AuthenticationMode = ‘NDID’
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
- If RMNo. Has value
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: If Fail to Create TSP Profile, OPO will not retry
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ channelTypeValue is not ‘na’ then continue to call H3: CustomerToAcctRel Inquiry - Else, Return Error
- Liveness Check If Yes, do face compare
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- [AuditLog] (Fail Only) Step 1 – NTB Registration – Create Customer Profile Temp
- 11. Select Authentication option
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- User Action : Select Authentication Option from [10D.1], [10D.2]
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] (Sucess/Fail) Step 18 - NTB Registration – Save KYC Info
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If AuthenticationMode = ‘NDID’
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- [AuditLog] (Fail Only) Step 19 - NTB Registration – Customer Search RM
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by ID Number. Else if RMNo has no value, then skip Get Customer Profile by ID Number and Continue to Call H13: CustomerRiskService-AMLRiskRating
- If RMNo. Has value
- [AuditLog] (Fail Only) Step 20 - NTB Registration – Get Customer Profile Remark: mask BAN
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/customer-profile/v2/internal/customers/inquiry", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] (Fail Only) Step 21 - NTB Registration – Check AML Risk Rating
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Create RMNO' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/echannel/profile", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- (NEW) H22: Update Segment Level ถ้า Fail ก็ Ignore แต่ยัง Update CIS เป็น A13 Request: RM No., Segment Level Response: Update datetime
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Update CustomerProfile' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/profiles/new-account-compliance", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] (Fail Only) Step 22 - NTB Registration – Create CIS Profile
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- If get daily total limit from oCRM error, then set segmentLevel (from oCRM) is A13
- Compare Segment & Daily Total Limit 1. Get daliyTotalLimit by segment (from RM) in configure D13 -> 30,000 2. Validate dailyTotalLimit If Max of dailyTotalLimit (from oCRM) >= dailyTotalLimit (from RM - H19), then set - segmentLevel = segmentLevel (from oCRM) D13, Otherwise, If get daily total limit from oCRM (H21) success, set - segmentLevel = 1st digit of segmentLevel (from oCRM) B + all digit exclude 1st digit of segmentLevel (from RM). Else, set segmentLevel = segmentLevel (from RM)
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- [ActivityLog] (Fail Only) Step 23 - NTB Registration – Update segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Compare Segment & Daily Total Limit” For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- [ActivityLog] (Sucess/Fail) Step 24 - NTB Registration – Create TSP Profile
- If allowPushFlag is ‘Y’, Else skip process
- [ActivityLog] (Sucess/Fail) Step 23 - NTB Registration – Create TSP Profile
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get Customer Profile
- [AuditLog] (Fail Only) Step 26 - NTB Registration – Get RM Account List
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Liveness Check If Yes, do face compare

## Decision Points

- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- [CIAM Validate] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B", the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B", the customer will be treated as non-suspicious.
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
- 11A.2 RTA-BeMyId Status Detail
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’ and ExpiryDateTime > DateTime.Now] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- 11B.4 RTA-NDID Status Detail
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
- Face Comparison Request: selfieImage Response: Status
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- If AuthenticationMode = ‘NDID’
- IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
- CIS_Wrapper (2) : Get Customer Profile by RM No POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: RMNO, {customerProfile, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, customerProfileEdd} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- If RMNo. Has value
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- Retry 3 times
- CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- 11B.4 NDID RTA status ‘Approved’
- 11A.2 BeMyID RTA status ‘Verified’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Liveness Check If Yes, do face compare
- Validate RTA Record If [RTAStatus = ‘Register’ or ‘Processing’] then,Return General Error Else, proceed next step to call Generate CustomerRefNo
- H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType (‘TC01’), durationOfTimeout(48hr from config), partnerId (‘04’) Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
- Validate Response If (H6) HTTP response code = 200 and responseCode = 000 Then, Insert DB with ReferenceId, IdNum, ProcessInstantKey, RTAId, RTACreateDateTime, RTAStatus = (status), RTAExpiryDateTime = (RTACreateDateTime+Duration Of Timeout)
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to next step H6: GenerateRTA-BeMyID Else if RTAStatus = ‘Locked’ or ‘Expired’ or ‘Rejected’ Then Skip H6 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
- Update DB with UpdateDateTime, RTA Status = ‘Cancelled’
- H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- Get RTA Status-BeMyId Request: ProcessInstantKey, ReferenceId, Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, RefCode, MachineName, RTAApprovedDateTime, ServicePointUrl
- If Customer Action: Tap ‘I’ve Enter My code’
- 10A.2 RTA-BeMyId Status Detail
- H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
- ‘Rejected’ RTAStatus = ‘Rejected’
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate RTAStatus If RTAStatus = ‘Register’ and ExpiryDateTime > DateTime.Now or RTAStatus = ‘Processing’ then, proceed next step to call (H7): InquiryRTA-BeMyID
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- RTA Status: ‘Verified’
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H7 as below: If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If ID Number is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If Issue Date is match then Set IssueDate_PassValidateFlag = ‘Y’ Else IssueDate_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- Validate IDP List If IDP has Preferred IDP Flag = ‘Y’ Then display IDP in section ‘Enrolled’ Elese, display in Section ‘Not Enrolled’
- 1. Get RTA List from OPO DB by CI If Count of ReferendId start with ‘NCBD_XXX’ >= 10 then, return Error Else continue Next to Get Latest RTA 2. Get Latest RTA Record by CI and ProcessInstantKey If RTAStatus = ‘Processing’ Then, Return General Error Else, proceed next step to call Generate ReferenceId
- H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- Validate Response If (H9) HTTP response code = 202 and RequestId has value Then, Insert DB with ReferenceId, RequestId, IDNum, ProcessInstantKey, UpdateDateTime, RTAStatus = ‘Processing’, RTACreateDateTime, CompanyCode, IndustryCode, appNameTh, appNameEn
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
- Validate Response If (H9) HTTP response code = 202 Update DB with UpdateDateTime, RTAStatus = ‘Cancelled’
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- If Customer Action: Tap ‘I’ve already authenticated’
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- Get RTA Status-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed next step to call (H10): Get RTA Status-NDID
- Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
- Validate RTA Expiry If Not Expired then, Proceed further Else, Update DB with UpdateDateTime, RTAStatus = ‘Expired’
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H10 as below: #To Be Revise If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If English First Name is match then Set FirstNameEN_PassValidateFlag = ‘Y’ Else FirstNameEN_PassValidateFlag = ‘N’ If English Last Name is match then Set LastNameEN_PassValidateFlag = ‘Y’ Else LastNameEN_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If ID is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- 10B.4 RTA-NDID Status Detail
- ‘Rejected’ RTAStatus = ‘Rejected’
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 4, if not, returns in-flow error (users can retry)
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
- [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
- Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
- 11A.2 RTA-BeMyId Status Detail
- [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- 11B.4 RTA-NDID Status Detail
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- [ActivityLog] Step 15 - NTB Registration – Get Customer Information Response2: Fail (Log Level1)
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
- [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
- [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
- IAM_24: Get profile from OPO Request: requestId, processInstanceKey Response: status
- Face Comparison Request: selfieImage Response: Status
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- If AuthenticationMode = ‘NDID’
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- IAM_20 Face Comparison Request: imageFile, requestId, requestChannel Response: status, Confidencescore, bblscore
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- CIS_Wrapper(4) (new): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
- [AuditLog] in case Fail/Success Only API Inquiry without JWT token
- Validate Response If status.code is “2005”, refer case “RMNo Has no Value” Otherwise, refer case “RMNo Has Value”
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
- Validate Response If RiskRating < 3, Then update Risk Level, Risk Reason Code into (Customer Profile Temp of OPO DB) proceed next step to Save State Expiry. Else, return error
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If identityVerifiedChannel = 002 beMyId
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- [AuditLog] in case Fail/Success Only CIS RM Update IAL
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- [AuditLog] in case Fail/Success Only API CREATE ACTION:
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- [AuditLog] in case Fail/Success Only Backend API Update PDPA
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result
- Prepare data for Call “H21: Get Daily Total Limit”. Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 4. RM Number Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now 2. RM Number from Response of “Create Customer Profile-NTB”
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
- [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. settingsDetails/transactionLimitScheme​ = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”“05”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- If Update Segment Level failed,
- [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
- Retry 3 times
- [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
- [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
- Check Permission of PushNotification OS If Enable, Continue Get Pushed Token Else, end process
- If Fail, then make pendingRegisterFlag is true
- CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
- CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {customerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
- 11B.4 NDID RTA status ‘Approved’
- 11A.2 BeMyID RTA status ‘Verified’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Liveness Check If Yes, do face compare
- POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3 - Add DWR Device profiling at beginning of onboarding and before request EFM to approval Remark: Since DWN charging model so decided to add at Entry - Add API call to EFM for request to approve - [#TBC] EFM Advice message via KAFKA
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- [CIAM App/OS version Checks] If OS version < OS minimal version return end-flow error If app version < app minimal version return end-flow (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade < today return end-flow error (force upgrade required) If app minimum <= app version < recommended minimal version and force upgrade >= today return in-flow error (recommended upgrade app version)
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NTB :transaction success | IA Cust Error Code: transaction fail Response:
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘IDCard’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 4, if not, returns in-flow error (users can retry)
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- IAM_06:Check Customer Suspicious Account Request: idType, idNum, name Response: status, dateTime, suspiciousCustomerInfo {idType, idNum, name, status, resultCode, resultDesc}
- [CIAM checks] If the suspiciousCustomerInfo attribute is present and contains a resultCode, CIAM will evaluate it. If resultCode = "B" or “W”, the customer is considered suspicious and CIAM will throw an error (blocked). If the resultCode has any value other than "B" or “W”, the customer will be treated as non-suspicious.
- [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- [CIAM Validate] If OTP matches, then can proceed futher
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPIN’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
- [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
- [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
- Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
- 11A.2 RTA-BeMyId Status Detail
- [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- 11B.4 RTA-NDID Status Detail
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- [ActivityLog] Step 15 - NTB Registration – Get Customer Information Response2: Fail (Log Level1)
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
- [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
- [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
- IAM_24: Get profile from OPO Request: requestId, processInstanceKey Response: status
- Face Comparison Request: selfieImage Response: Status
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- If AuthenticationMode = ‘NDID’
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- IAM_20 Face Comparison Request: imageFile, requestId, requestChannel Response: status, Confidencescore, bblscore
- CIAM checks bblscore. If it equals to 3, then can proceed further
- POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- CIS_Wrapper(4) : Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
- [AuditLog] in case Fail/Success Only API Inquiry without JWT token
- Validate Response If status.code is “2005”, refer case “RMNo Has no Value” Otherwise, refer case “RMNo Has Value”
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
- Validate Response If RiskRating < 3, Then update Risk Level, Risk Reason Code into (Customer Profile Temp of OPO DB) proceed next step to Save State Expiry. Else, return error
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If identityVerifiedChannel = 002 beMyId
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- [AuditLog] in case Fail/Success Only CIS RM Update IAL
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- [AuditLog] in case Fail/Success Only API CREATE ACTION:
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’: transaction success | OPO Cust Error Code: transaction fail Response:
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- [AuditLog] in case Fail/Success Only Backend API Update PDPA
- If API update Host or Kafka fail, re execute fail process (retry X times)
- Write fail payload to DB
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result
- Prepare data for Call “H21: Get Daily Total Limit”. Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 4. RM Number Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now 2. RM Number from Response of “Create Customer Profile-NTB”
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
- [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- If Update Segment Level failed,
- [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
- Retry 3 times
- [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
- [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
- If Fail, then make pendingRegisterFlag is true
- CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
- CIS_Wrapper (10): Get Customer Account Relationship Request: RM No., {customerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
- 11B.4 NDID RTA status ‘Approved’
- 11A.2 BeMyID RTA status ‘Verified’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value - If CISID has value and value in x-channel exist in channelTypeValue and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ then check has IA profile. If it true then, continue at Reactivate Flow - Else if CISID has value and value in x-channel exist in channelTypeValue and doesn’t have IA profile. If it true then, continue at ETB flow - CIAM set MISSING_IDM_Profile flag in nodeState. - Else If CISID has no value or CISID has value and value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Liveness Check If Yes, do face compare
- CIS_Wrapper: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- If CIS profile not found or CIS status is invalid, search RM
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(48hr from config), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
- H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
- RTA Status = ‘Verified’
- H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
- H9: GenerateRTA-NDID URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- 10B.4 NDID RTA status ‘Approved’
- H10: Get RTA Status-NDID URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, BAN
- If: No CIS ID, No RM Profile
- H13: CustomerProfileIALMod Request: RM no., IAL Response: status, result
- If: No CIS ID, Has RM Profile
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- Prepare data for Call “H21: Get Daily Total Limit”. Fields from Response of “Create Customer Profile-NTB” 1. RM Number Fields below use from customer enter (Customer Profile Temp from OPO DB) 1. Occupation Code 2. Education Code 3. Income Code 4. CT Code 5. Risk Level 6. Risk Reason Code 7. Risk Occupations 1 8. Earning from countries 1-3 9. Place of Birth 10. Nationalities 1 11. Date of Birth If RMNo Has value (from Response of H19), Fields below use from H19 1. First Contact Date 2. Nationalities 2-3 3. Risk Occupations 2-3 Else If RMNo Has no value (from Response of H19), Fields below use 1. First Contact Date – Default with DateTime.Now
- H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- Validate Response 1. HTTP code = 200 and responseCode = 000 2. Check RTA Status
- Validate Response FaceCompare result
- Validate RTA Record If [RTAStatus = ‘Register’ or ‘Processing’] then,Return General Error Else, proceed next step to call Generate CustomerRefNo
- H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType (‘TC01’), durationOfTimeout(48hr from config), partnerId (‘04’) Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
- Validate Response If (H6) HTTP response code = 200 and responseCode = 000 Then, Insert DB with ReferenceId, IdNum, ProcessInstantKey, RTAId, RTACreateDateTime, RTAStatus = (status), RTAExpiryDateTime = (RTACreateDateTime+Duration Of Timeout)
- [AuditLog] Step 4 - NTB Registration - Create BeMyId RTA Response1: Success Response2: Fail
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to next step H6: GenerateRTA-BeMyID Else if RTAStatus = ‘Locked’ or ‘Expired’ or ‘Rejected’ Then Skip H6 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
- Update DB with UpdateDateTime, RTA Status = ‘Cancelled’
- H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
- [AuditLog] Step 5 - NTB Registration – Cancel BeMyId RTA Response1: Success Response2: Fail
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- [ActivityLog] Step 5 - NTB Registration – Cancel BeMyId Request Response1: Success (Log level2) Response2: Fail (Log Level1)
- Get RTA Status-BeMyId Request: ProcessInstantKey, ReferenceId, Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, RefCode, MachineName, RTAApprovedDateTime, ServicePointUrl
- If Customer Action: Tap ‘I’ve Enter My code’
- 10A.2 RTA-BeMyId Status Detail
- H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
- ‘Rejected’ RTAStatus = ‘Rejected’
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate RTAStatus If RTAStatus = ‘Register’ or ‘Processing’ then, proceed next step to call (H7): InquiryRTA-BeMyID
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Register’ or ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- [AuditLog] Step 6 - NTB Registration – Check BeMyId RTA Status Response1: Success Response2: Fail
- RTA Status: ‘Verified’
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H7 as below: If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If ID Number is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If Issue Date is match then Set IssueDate_PassValidateFlag = ‘Y’ Else IssueDate_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- [ActivityLog] Step 7 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : Null NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_DipChip’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] Step 8 - NTB Registration – Get NDID TC Response1: Success Response2: Fail
- [AuditLog] Step 9 - NTB Registration – NDID TC Acceptance Response1: Success Response2: Fail
- Validate IDP List If IDP has Preferred IDP Flag = ‘Y’ Then display IDP in section ‘Enrolled’ Elese, display in Section ‘Not Enrolled’
- [AuditLog] Step 10 - NTB Registration – GetIDPBankList Response1: Success Response2: Fail
- 1. Get RTA List from OPO DB by CI If Count of ReferendId start with ‘NCBD_XXX’ >= 10 then, return Error Else continue Next to Get Latest RTA 2. Get Latest RTA Record by CI and ProcessInstantKey If RTAStatus = ‘Processing’ Then, Return General Error Else, proceed next step to call Generate ReferenceId
- H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- Validate Response If (H9) HTTP response code = 202 and RequestId has value Then, Insert DB with ReferenceId, RequestId, IDNum, ProcessInstantKey, UpdateDateTime, RTAStatus = ‘Processing’, RTACreateDateTime, CompanyCode, IndustryCode, appNameTh, appNameEn
- [AuditLog] Step 11 - NTB Registration – Create NDID RTA Response1: Success Response2: Fail
- If Customer Action: Tap ‘Change Method’
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
- Validate Response If (H9) HTTP response code = 202 Update DB with UpdateDateTime, RTAStatus = ‘Cancelled’
- [AuditLog] Step 12 - NTB Registration – Cancel NDID RTA Response1: Success Response2: Fail
- Mapping FlowType 1. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’
- Validate Flow Type to Display If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2]
- If Customer Action: Tap ‘I’ve already authenticated’
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- Get RTA Status-NDID Request: ProcessInstantKey, ReferenceId Response: ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed next step to call (H10): Get RTA Status-NDID
- [AuditLog] Step 13 - NTB Registration – Check NDID RTA Status Response1: Success Response2: Fail
- Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
- Validate RTA Expiry If Not Expired then, Proceed further Else, Update DB with UpdateDateTime, RTAStatus = ‘Expired’
- 1. Get Latest RTA Record by CI and ProcessInstantKey 2. Validate Existing RTA Status before Update New RTA Status If RTAStatus = ‘Processing’ Then, proceed to update RTAStatus, UpdateDate to DB
- If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
- Validate Post Authentication by Compare match value of User Temp Profile and AS_Data from H10 as below: #To Be Revise If Thai First Name is match then Set FirstNameTH_PassValidateFlag = ‘Y’ Else FirstNameTH_PassValidateFlag = ‘N’ If Thai Last Name is match then Set LastNameTH_PassValidateFlag = ‘Y’ Else LastNameTH_PassValidateFlag = ‘N’ If English First Name is match then Set FirstNameEN_PassValidateFlag = ‘Y’ Else FirstNameEN_PassValidateFlag = ‘N’ If English Last Name is match then Set LastNameEN_PassValidateFlag = ‘Y’ Else LastNameEN_PassValidateFlag = ‘N’ If Date of Birth is match then Set BirthDate_PassValidateFlag = ‘Y’ Else BirthDate_PassValidateFlag = ‘N’ If ID is match then Set ID_PassValidateFlag = ‘Y’ Else ID_PassValidateFlag = ‘N’ If All above XX_PassValidate = ‘Y’ then Set InvalidFlag = ‘N’ Else, Set InvalidtFlag = ‘Y’ and InvalidReason = ‘AuthenFailed’
- 10B.4 RTA-NDID Status Detail
- ‘Rejected’ RTAStatus = ‘Rejected’
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- [ActivityLog] Step 14 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_NDID’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page Else if
- Check CIAM Channel Status - Locked => PIN locked alert - Active => Proceed next step
- CIAM checks 1. Validate DPoP proof - validate auth 2. Access Token is valid or not 3. Channel status - Locked > PIN locked alert - Active > Go to next step 4. PIN is valid or not
- 1. Get Current Save State 2. Validate Save state Expiry à If Save state is not expired, Then Return currentState à Else if Save state is expired or could not find save state, then Return error ERR_OPO_COM_034
- Validate Response If currentState in state 1, then continue to call Get RTA List from OPO DB Else if currentState in state 2, then continue to call Get KYC Lookup Data
- If Save State = 1 then, direct customer to Get RTA List from OPO DB
- If Save State = 2 then, direct customer to KYC
- If Save State = 3 then, direct customer to product origination
- POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page Else if
- Check CIAM Channel Status - Locked => PIN locked alert - Active => Proceed next step
- CIAM checks 1. Validate DPoP proof - validate auth 2. Access Token is valid or not 3. Channel status - Locked > PIN locked alert - Active > Go to next step 4. PIN is valid or not
- 1. Get Current Save State 2. Check CIS ID in customer prospect table à If CIS ID have value, return error ERR_OPO_NTB_043. à Otherwise, continue to proceed No.3 3. Validate Save state Expiry à If Save state is not expired, Then Return currentState à Else if Save state is expired or could not find save state, then Return error ERR_OPO_COM_034
- Validate Response If currentState in state 1, then continue to call Get RTA List from OPO DB Else if currentState in state 2, then continue to call Get KYC Lookup Data
- If Save State = 1 then, direct customer to Get RTA List from OPO DB
- If Save State = 2 then, direct customer to KYC
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- [CIAM Validate] CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- [AuditLog] in case Fail Only Step 7 - NTB Onboarding - Laser Code - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- [AuditLog] (Fail Only) Step 1 – NTB Registration – Create Customer Profile Temp
- Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
- 11A.2 RTA-BeMyId Status Detail
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- 11B.4 RTA-NDID Status Detail
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] (Sucess/Fail) Step 18 - NTB Registration – Save KYC Info
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
- Face Comparison Request: selfieImage Response: Status
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- If AuthenticationMode = ‘NDID’
- IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- [AuditLog] (Fail Only) Step 19 - NTB Registration – Customer Search RM
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
- If RMNo. Has value
- CIS_Wrapper (2) : Get Customer Profile by RM No POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: RMNO, {customerProfile, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, customerProfileEdd} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- [AuditLog] (Fail Only) Step 20 - NTB Registration – Get Customer Profile
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] (Fail Only) Step 21 - NTB Registration – Check AML Risk Rating
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Create RMNO' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/echannel/profile", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Update CustomerProfile' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/profiles/new-account-compliance", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = <env>.raw.cis.party.create - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- [AuditLog] (Fail Only) Step 22 - NTB Registration – Create CIS Profile
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = <env>.raw.cis.party.create/ <env>.raw.cis.party.update - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = Map <Kafka topic name> - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- If found duplicate mobile no.
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = Map <Kafka topic name> - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = n/a - alternateIdType = n/a - alternateId = n/a - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = `Batch’ - actType = 'Batch from CIS' - actSubType = 'Batch Add Relationship to RM'/ 'Batch Update Mobile Number to RM' - actStatus = Batch file transfer result (Exit Code) - errorCode = batch_job_execution.exit_code - errorMessage = batch_job_execution.exit_message (first 200 char) - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = แต่ละ step ของ Batch
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- Retry 3 times
- [ActivityLog] (Sucess/Fail) Step 23 - NTB Registration – Create TSP Profile
- If allowPushFlag is ‘Y’, Else skip process
- CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] (Fail Only) Step 24 - NTB Registration – Get Customer Profile
- CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List
- 11B.4 NDID RTA status ‘Approved’
- 11A.2 BeMyID RTA status ‘Verified’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Liveness Check If Yes, do face compare
- CIS_Wrapper: Customer Search by Citizen ID Request: idNum Response: DoB, RM No. or CIS No., CIS status
- If CIS profile not found or CIS status is invalid, search RM
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- H6: GenerateRTA-BeMyID URL:[MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(48hr from config), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}
- H6: GenerateRTA-BeMyID URL: [MASKED_URL] Request: customerRefNo, idNumber, idType, transactionType, durationOfTimeout(0hr), partnerId Response: responseCode, responseMesg, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status, idNumber, idType, transactionType}:
- RTA Status = ‘Verified’
- H7: InquiryRTA-BeMyID URL: [MASKED_URL] Request:idNumber, idType, rtaId, transactionType, partnerId Response: responseCode, responseMesg, transactionTyoe, dopaResultCode, dopaResultDesc, machineName, cardInfo {idType, idNumber, cardVersion, cardNo, chipId,laserId, titleNameTh, firstNameTh, middleNameTh, lastNameTh, titleNameEn, firstNameEn, middleNameEn, lastNameEn, birthDate, gender, issuePlace, issueCode, issuerSignature, issueDate, expiryDate, photoFile, photoCodeNo, address}, rtaInfo {rtaId, rtaCreateDateTime, durationOfTimeout, status,bblDipChipDateTime, bblOnlineDopaDateTime, customerRefNo}
- H9: GenerateRTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request Request: Reference Id, Citizen Id, request_message_en, request_message_th, min_ial, min_aal, min_idp, request_timeout(3600), mode(2), idp_id_list, bypass_identity_check (if Preferred IDP Flag is ‘N’, Set TRUE), data_request_list {service_id(001.cust_info_001),request_params} Response: request_id
- 10B.4 NDID RTA status ‘Approved’
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- If RMNo. Has value
- If: No CIS ID, No RM Profile
- If: No CIS ID, Has RM Profile
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- Validate Response 1. HTTP code = 200 and responseCode = 000 2. Check RTA Status
- Validate Response FaceCompare result
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] 1. Detection Score >= 0.6 If < 0.6, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- [CIAM Validate] CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
- 10A.2 RTA-BeMyId Status Detail
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- 10B.4 RTA-NDID Status Detail
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
- Face Comparison Request: selfieImage Response: Status
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- If AuthenticationMode = ‘NDID’
- IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by RMNo. Else if RMNo has no value, then skip Get Customer Profile by RMNo.and Continue to Call H13: CustomerRiskService-AMLRiskRating
- CIS_Wrapper (2) : Get Customer Profile by RM No Request: RMNO, {customerProfile, customerProfileDetails, customerProfileAddress, customerProfileContactInfo, customerProfileIalInfo, customerProfileKyc, customerProfileTaxReportInfo, customerProfileEdd, contactNumber, identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- If RMNo. Has value
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H18 First Account Date = firstAccountDate from response of H18 Existing Risk Level = riskLevel from response of H18 Existing Risk Level Reason Code = riskReasonCode from response of H18 Good Guy Flag = goodGuyFlag from response of H18 Nationality2 = nationalityCode2 from response of H18 Nationality3 = nationalityCode3 from response of H18 Type of Business2 = riskOccupationCode2 from response of H18 Type of Business3 = riskOccupationCode3 from response of H18 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H18 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- If found duplicate mobile no.
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: If Fail to Create TSP Profile, OPO will not retry
- CIS_Wrapper (2) : Get Customer Profile by CIS ID Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- 10B.4 NDID RTA status ‘Approved’
- 10A.2 BeMyID RTA status ‘Verified’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ channelTypeValue is not ‘na’ then continue to call H3: CustomerToAcctRel Inquiry - Else, Return Error
- Liveness Check If Yes, do face compare
- Check Digital ID in secure storage If there is no digital id in secure storage go to First Page
- TBC: If customer begin this step again after save state expired, would this cache is still has value in cache?
- Validate time is not in Period off host (02:00-04:00) > Period should be configurable. if True, return error.
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- CIAMService-AcceptT&C Request: Approve to accept Response: prompt citizen ID, prompt DOB
- CIS_Wrapper (1): Customer Search by Citizen ID POST: /customerprofile/api/v2/cis/internal/customers/inquiry Request: idNum, {customerSearch} Response: status, cisid, partyBlockedStatus, channels {channelTyoe, channelTypeValue, partyChannelStatus, partyChannelBlock}, rmNumber, dob
- If CIS profile not found or CIS status is invalid, search RM
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [ActivityLog] Step 6 - NTB Onboarding - Submit data to OCR - Response 6 - Response with Laser Code - Response 4.1 - User clicks go back to PDPA - In flow error Response 6.1 - Retry OCR - End flow - Customized error - End flow - OOTB error
- [CIAM Validate] 1. Detection Score >= 0.8 If < 0.8, returns full screen error 2. CI match with CI that user input in page 3, if not, returns full scree error
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] Response code = 0 and desc = ‘สถานะปกติ’ Then, can proceed further *User can retry up to 5 times
- IAM_06: Check Customer Suspicious Account Request: idType, idNum, name Response: status, result, dateTime
- [CIAM Validate] CIAM checks result: contains only “dateTime” and no “suspiciousCustomerInfo”. Then, can proceed further
- [AuditLog] in case Fail Only IAM Proxy sheet - IAM_06 Response
- [ActivityLog] Step 7 - NTB Onboarding - Laser Code - Response 7.1 - Response with OTP - In flow error Response 7.2 - 1-4 Failed Laser code Validation - End flow - Customized error - End flow - OOTB error
- H5: SendSMS POST:/notification-services/sms/send Request: MobileNo., Message Response: Response code, Result, ResultDescription
- IAM_08: Send SMS OTP Request: mobileNum, smsLanguage Response: status
- [CIAM Validate] If OTP matches, then can proceed futher
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- If OPO returns error, end the flow.
- Create Customer Profile Record (Temp) Request: ProcessInstantKey, IdNum, idType, ThaiTitle Name, ThaiFirstName, ThaiLastName, EnglishTitleName, EnglishFirstName, EnglishLastName, DateofBirth, IDExpiryDate, IDIssueDate, TnCAcceptanceFlag, TnCAcceptDateTime, TnCVersion, PDPAFlag, PDPAPurposeCode, PDPAConsentDateTime,DOPADateTime, MobileNumber, Nationality, CTCode, CustomerType, Gender(from Title), CountryOfResidence, PlaceOfBirth Response: Remark: Orange Line are fields that OPO need to Fixed value by following condition Nationality : ‘TH’ CTCode : ‘09’ CustomerType: ‘P’ CountryOfResidence: ‘TH’ PlaceOfBirth: ‘TH’ Gender: If Title = ‘Mr.’ then Gender = ‘M’ Else if Title = ‘Miss’ or ‘Mrs.’ then ‘F’
- Create DigitalID Profile with 1. CIS ID= Null 2. ProcessInstantKey **EOD Process to​ clean up Digital ID profile that CIS ID = Null when create date > 7 days​
- [AuditLog] (Fail Only) Step 1 – NTB Registration – Create Customer Profile Temp
- Get RTA List from OPO DB (Fetch Task with Data return) Request: ProcessInstantKey Response: flowType, BeMyID {ReferenceId, RTA status, RTAExpiryDatetime, RTACreatedDateTime, CustomerRefNo, machineName, RTAApprovedDateTime, ServicePointUrl}, NDID {ReferenceId, RTAStatus, RTAExpiryDatetime, RTACreatedDateTime, appNameTh, appNameEn, RTAApprovedDateTime, WarningMessageTH, WarningMessageEN, IDPBankLogoUrl}
- 11A.2 RTA-BeMyId Status Detail
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Verified’ and InvalidFlag = ‘Y’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- If has RTA Exist, ReferenceId Start with B_XX and ‘Registered’ or [RTAStatus = ‘Processing’]
- If has RTA Exist, ReferenceId Start with NCBD_XX and ‘ If [RTAStatus = ‘Processing’]
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- 11B.4 RTA-NDID Status Detail
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If Customer Search Address
- If Customer Search Country for Earning Country
- If Customer Tap ‘Next’ at Each page
- If Customer select Occupation 001,002,003,004,005 Screen will display Office Position field, Name of Employer fields, Address section, Office phone Number to customer Else, screen will hiding all above related to working details
- If Customer select box ‘Same as Citizen ID Card address’ in [11.2] Mailing address Then, System will automatically copy address information from Citizen ID Card address section to display in Mailing address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- [ActivityLog] (Sucess/Fail) Step 18 - NTB Registration – Save KYC Info
- If Customer select box ‘Same as Citizen ID Card address’ or ‘Same as Current address’ in [11.3] Office address section Then, System will automatically Copy address information from Citizen ID Card address or Current address to display in Office address section with disable customer to edit - Address Line1 - Address Line2 - Sub-district, district, province, and postal code
- IAM_24 (new): Get profile from OPO - Validate: has profile in OPO or not?, do eKYC? Header: ProcessInstantKey Request: requestId Response: status
- Face Comparison Request: selfieImage Response: Status
- H10: Get RTA Status-NDID [New Service] URL: Get /NDIDSwagger/RPServices/rp/request/v3/referenceID/{reference_id} Request: reference_id Response: guid, reference_id, namespace, identifier_no, input_date, request_id, ndid_mode, request_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_as_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, request_timeout, status, status_date, request_message_th, request_message_en, ndid_status, ndid_status_date, error_code, data_salt, cust_action, cust_action_date, node_id, answered_idp_list{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, data_request_list{as_node_id, as_node_name_th, as_node_name_en, answered_as{node_id, max_ial, max_aal, min_ial, min_aal, industry_code, company_code, marketing_name_th, marketing_name_en, proxy_or_subsidiary_name_th, proxy_or_subsidiary_name_en, role, running, error_code}, service_id, data, request_params}, block_height, creation_block_height, create_request_date
- If AuthenticationMode = ‘NDID’
- IAM_20 Face Comparison Request: selfieImage, requestId(x-transaction-id), requestChannel Response: status, Confidencescore, bblscore
- H12: FaceRecognitionCompare POST: /smartcard/face-recognition/compare Request: IdNumber, RequestType, ImageFile1, ImageSourceType1,RequestId, RequestChannel, StoreTemplateType, StoreTemplateFile, ImageFile2, ImageSourceType2 Response: Status, RequestId, Confidencescore, bblscore, ErrorDescription
- CIAM checks bblscore. If it equals to 3, then can proceed further
- If fail
- [ActivityLog] Step 3 - NTB Onboarding Face Verification - Selfie picture - In flow error Response 2.1 - 1-4 Face Invalid attempts - End flow - Customized error - End flow - OOTB error IAM Proxy sheet - IAM_20 Response
- If face compare failed 5 times, Display Full screen error. Deep link to 0B. First Page and has Digital ID.
- Validate Off Host time If Time.Now in 07:00 A.M. – 10:00 P.M. (in application config – need to restart service and not impact to down time) ,Then proceed next step to Create Customer Profile at CIS Else, return error
- If pass face compare
- [AuditLog] (Fail Only) Step 19 - NTB Registration – Customer Search RM
- Validate Response If RMNo has value, then Continue to Call Get Customer Profile by ID Number. Else if RMNo has no value, then skip Get Customer Profile by ID Number and Continue to Call H13: CustomerRiskService-AMLRiskRating
- CIS_Wrapper() (new): Get Customer Profile (BAN) POST: /cis/customer-profile/v2/internal/customers/inquiry (No token) Request: idType, idNum, ProfileOption=Full, {customerProfileBan} Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, Segment, BAN
- If RMNo. Has value
- (NEW) H19: BBLOwnCustCheckInq POST: /esis/customer-services/customers/bbl-own-customer/check Request: ID Type, ID Number, ProfileOption=Full Response: RM, First Contact Date, Nationality 1-3, Date of Birth, Occupation, Sub Occupation, Education, Income, CT Code, Risk Level, Risk Reason Code, Risk Occupations 1-3, Earning Country 1-3, Place of Birth, IAL, First name, Last name, Mobile, Profile status, Channel Status, Segment, BAN
- [AuditLog] (Fail Only) Step 20 - NTB Registration – Get Customer Profile Remark: mask BAN
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/customer-profile/v2/internal/customers/inquiry", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Additional Mapping Fields for Request H13: If RMNo Has value Map fields: RM Number = RMNo. from response of H19 First Account Date = firstAccountDate from response of H19 Existing Risk Level = riskLevel from response of H19 Existing Risk Level Reason Code = riskReasonCode from response of H19 Good Guy Flag = goodGuyFlag from response of H19 Nationality2 = nationalityCode2 from response of H19 Nationality3 = nationalityCode3 from response of H19 Type of Business2 = riskOccupationCode2 from response of H19 Type of Business3 = riskOccupationCode3 from response of H19 *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = nameEN from response of H19 Else if RMNo Has no value Map fields: RM Number = blank First Account Date = Not send Existing Risk Level = Not send Existing Risk Level Reason Code = Not send Good Guy Flag = Not send *Other fields map from OPO Customer Profile Temp Thai Fullname = [Thai Title Name] + “ ” + [Thai First Name] + “ ” + [Thai Last Name] English FullName = [English Title Name] + “ ” + [English First Name] + “ ” + [English Last Name]
- [AuditLog] (Fail Only) Step 21 - NTB Registration – Check AML Risk Rating
- Validate Response If RiskRating < 3, Then proceed next step to Check Off Host period Else, return error
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- If: No RM Profile (Create CISID, Create RMNO)
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Create RMNO' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/echannel/profile", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- (NEW) H22: Update Segment Level ถ้า Fail ก็ Ignore แต่ยัง Update CIS เป็น A13 Request: RM No., Segment Level Response: Update datetime
- If: Has RM Profile (Create CISID, Update RM Profile)
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- H18: CustomerProfileInq POST: /esis/customer-services/customers/profile/inquiry Request: RM No. Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupation, Monthly Income, Education, First Contract Date, Office Name, Job Position, Place of Birth, BBL IAL, Risk Level, Risk Reason Code, EDD Status, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code,Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version, KYC Update Sate, Face To Face Flag, BBL-IAL Last Maintenance date, IDP-IAL Code, IDP-IAL Last Maintenance date, IDP-Customer Creation
- H15: Update Customer KYC at RM POST: Request: RMNum, Marital Status, Education, Monthly Income, Mailing Address, Office Address, ID Address, Office Name, Position, Occupation, Contact Number, Contact Extension, Mobile Number, Office Phone Number, Office Phone Extension, Risk Level, Risk Reason Code, Risk Update Date, Risk Update By, KYC Last Maintenance date, Source of Asset, Value of Asset, Earning of country 1-3, Type of Business 1-3, Classification, Classification Update By, Classification Date, Nationality 1-3, Country of Birth, Green Card Flag, Substantial presence test flag, Face to Face flag, BBL IAL, BBL-IAL Last Maintenance date, BBL IAL Update By, IDP IAL, IDP-IAL Last Maintenance date, IDP Bank Code, IDP Customer Creation, Market Consent Flag, Market Consent Date, Market Consent Update By, CRS Flag Response: Error Flag, Error Description, Transaction Date Time
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = IdType - alternateId = IdNumber - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Update CustomerProfile' - actStatus = API response status - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/esis/customer-services/customers/profiles/new-account-compliance", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = <env>.raw.cis.party.create - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- [AuditLog] (Fail Only) Step 22 - NTB Registration – Create CIS Profile
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = <env>.raw.cis.party.create/ <env>.raw.cis.party.update - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- H16: CustomerService-CustomerProfileRelAdd POST:/cbrm-services/customers/accounts/relationship Request: rmNum, relationshipCode, accountControlCode, appId, accountNum(CISID) Response: status, result Remark: This service to create Relationship CISID with RM Profile
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- H17: PDPAConsentUpdate POST: /PDPA/bbl-devices/consent/update Request: IdType, IdNumber, ConsentDate, PurposeCustomerConsent, Flag Response: Status, ErrorCode, ErrorDescription
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- If API update CustomerProfileRelAdd fail
- E3:Publish Event topic: <env>.cis.api.service.failed EventType: FAIL_RM_CIS_ADD_REL
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Check if duplicate mobile no. in CIS Profile
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_PUBLISH' - actSubType = Map <Kafka topic name> - actStatus = Kafka event publish result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- If found duplicate mobile no.
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId - alternateIdType = n/a - alternateId = n/a - initiateBy = Filled by common lib - bblTraceId = metadata.eventId - actSource = `NCCI’ - actGroup = `KafkaEvent’ - actType = 'KAFKA_EVENT_CONSUME' - actSubType = Map <Kafka topic name> - actStatus = Kafka event consume result - errorCode = errorCode - errorMessage = errorMessage - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = n/a
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- [AuditLog] - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = n/a - alternateIdType = n/a - alternateId = n/a - initiateBy = n/a - bblTraceId = n/a - actSource = `NCCI’ - actGroup = `Batch’ - actType = 'Batch from CIS' - actSubType = 'Batch Add Relationship to RM'/ 'Batch Update Mobile Number to RM' - actStatus = Batch file transfer result (Exit Code) - errorCode = batch_job_execution.exit_code - errorMessage = batch_job_execution.exit_message (first 200 char) - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Kafka payload - auditData = แต่ละ step ของ Batch
- (NEW) H21: Get Daily Total Limit POST: /ocrm-services/customer-profiling/customers/daily-limit/kyc/inquiry Request: firstContactDate, nationalities, dateOfBirth, occupationCode, educationCode, incomeCode, ctCode, riskLevel, riskReasonCode, riskOccupations, earningFromCountries, placeOfBirth, rmNumber Response: isError, result {allowableLimitSet: segmentLevel, dailyTotalLimit}, error
- If get daily total limit from oCRM error, then set segmentLevel (from oCRM) is A13
- Compare Segment & Daily Total Limit 1. Get daliyTotalLimit by segment (from RM) in configure D13 -> 30,000 2. Validate dailyTotalLimit If Max of dailyTotalLimit (from oCRM) >= dailyTotalLimit (from RM - H19), then set - segmentLevel = segmentLevel (from oCRM) D13, Otherwise, If get daily total limit from oCRM (H21) success, set - segmentLevel = 1st digit of segmentLevel (from oCRM) B + all digit exclude 1st digit of segmentLevel (from RM). Else, set segmentLevel = segmentLevel (from RM)
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- [ActivityLog] (Fail Only) Step 23 - NTB Registration – Update segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = segmentLevel of step “Compare Segment & Daily Total Limit” For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- [ActivityLog] (Sucess/Fail) Step 24 - NTB Registration – Create TSP Profile
- If allowPushFlag is ‘Y’, Else skip process
- [ActivityLog] (Sucess/Fail) Step 23 - NTB Registration – Create TSP Profile
- CIS_Wrapper (2) : Get Customer Profile by CIS ID POST: /customerprofile/api/v2/cis/customers/details Request: CISID, {CustomerProfile, CustomerProfileDetails, CustomerProfileAddress, CustomerProfileContactInfo, CustomerProfileIalInfo, CustomerProfileKyc, CustomerProfileTaxReportInfo, CustomerProfileEdd, ContactNumber, Identifier} Response: RM No., ID Type, ID Number, DOB, Mailing Address, Office Address, Contact Number, Mobile Number, Office Phone Number, CT Code, Nationality 1-3, Country of residence, Marital Status, Occupstion, Monthly Income, Education, First Account Date, Office Name, Job Position, Place of Birth, , BBL IAL, Risk Level, Risk Reason Code, EDD Statue, EDD Next Due Date, CRS Info, Source of asset, Value of asset, Earning of country1-3, Type of business1-3, Good Guy Flag, Classification Code, , Green Card Flag, Substantial presence test flag, Market Consent Flag, Market Consent Version
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get Customer Profile
- CIS_Wrapper (1): Get Customer Account Relationship Request: RM No., {CustomerAccountRelationship} Response: Account Number, Account status, acctControl1, appId, relationshipCode, accountProdCode, acctControl2, acctControl3, acctControl4, NCBD Account Type
- [AuditLog] (Fail Only) Step 26 - NTB Registration – Get RM Account List
- 11B.4 NDID RTA status ‘Approved’
- 11A.2 BeMyID RTA status ‘Verified’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Register Device Notification Request: CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Register Device Notification Request: appId = ‘na’, CIAMToken ,deviceId ,pushToken ,platform ,appVersion ,osVersion Response: status, refCode, deviceRefId
- Liveness Check If Yes, do face compare

## Success Markers

- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’ and ExpiryDateTime > DateTime.Now] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If pass face compare
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- 11B.4 NDID RTA status ‘Approved’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
- If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
- [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
- [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
- [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
- [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
- [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
- [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
- If pass face compare
- [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
- [AuditLog] in case Fail/Success Only API Inquiry without JWT token
- [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only CIS RM Update IAL
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- [AuditLog] in case Fail/Success Only API CREATE ACTION:
- [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
- [AuditLog] in case Fail/Success Only Backend API Update PDPA
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
- [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. settingsDetails/transactionLimitScheme​ = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”“05”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
- [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
- [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
- [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
- 11B.4 NDID RTA status ‘Approved’
- CDP3: Update Onboard success
- POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3 - Add DWR Device profiling at beginning of onboarding and before request EFM to approval Remark: Since DWN charging model so decided to add at Entry - Add API call to EFM for request to approve - [#TBC] EFM Advice message via KAFKA
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [AuditLog] in case Fail/Success Only CIS Inquiry Wrapper with no token
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old and < 100 and not a future date) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘PersonalInfo’ TransactionSubType = NTB :transaction success | IA Cust Error Code: transaction fail Response:
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘IDCard’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SmsOtp’ TransactionSubType = NTB: transaction success | IA Cust Error Code: transaction fail Response:
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘SetPIN’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
- [AuditLog] Step 1 – NTB Registration – Create Customer Profile Temp Response1: Success create customer profile temp Response2: Fail
- [ActivityLog] Step 2 – NTB Registration – Create Customer Profile Temp Response1: Success (Log Level2) Response2: Fail (Log Level1)
- [ActivityLog] Step 3 – NTB Registration – Get Verification Option Response1: Success (Log Level2) Response2: Fail (Log Level1)
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- [AuditLog] Step 16 - NTB Registration – Save KYC Info1 Response1: Success Response2: Fail
- [AuditLog] Step 17 - NTB Registration – Save KYC Info2 Response1: Success Response2: Fail
- [AuditLog] Step 18 - NTB Registration – Save KYC Info3 Response1: Success Response2: Fail
- [AuditLog] Step 19 - NTB Registration – Save KYC Info4 Response1: Success Response2: Fail
- [ActivityLog] Step 20 - NTB Registration – Save KYC Info Response1: Success (Log level2) Response2: Fail (Log Level1)
- POST:/efm-services/transaction Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’:transaction success | IA Cust Error Code: transaction fail Response:
- If pass face compare
- [AuditLog] Step 21 - NTB Registration – Get Customer Profile Remark: mask BAN. Response1: Success Response2: Fail
- [AuditLog] in case Fail/Success Only API Inquiry without JWT token
- [AuditLog] Step 22 - NTB Registration – Check AML Risk Rating Response1: Success Response2: Fail
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only CIS RM Update IAL
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- [AuditLog] in case Fail/Success Only API CREATE ACTION:
- [AuditLog] Step 23 - NTB Registration – Create CIS Profile Response1: Success Response2: Fail
- [ActivityLog] Step 24 - NTB Registration – Create CIS Profile Response1: Success (Log Level1) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL: fail to create profile| CISID: Success to create profile NCBD Registered E-mail : Registered Email (If Any) NCBD Registered Phone Number : Registered MobileNo. NCBD User first log on : SystemDatetime NCBD registration date : SystemDatetime Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 0:Not use EFM decision TransactionType = ‘FaceScanandCreateCIS’ TransactionSubType = ‘NTB’: transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] in case Fail/Success Only Backend API RM Add Relationship
- [AuditLog] in case Fail/Success Only Backend API Update PDPA
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- CIS_Wrapper(15) (new): Update Segment Level POST /cis/customer-profile/v2/internal/customers/inquiry (No token): Request: CIS ID, Segment Level, BAN (optional) Action: UPDATE_CLASSIFICATION Response: success/fail
- [AuditLog] in case Fail/Success Only Backend API RM Update Customer Segment
- TSP1: Create TSP Profile Request: Salutation, first name, last name, user segment, CISID Response: firstName, middleName, lastName, userID, customerId Remark: userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, use 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “A”. userDetails/otherRetailDetails/segmentName = below rules - If “H21: Get Daily Total Limit” success, All digits except 1st digit of segmentLevel from step “Update Segment Level” - Otherwise, use “13”. For other field map below field from OPO Customer Profile Temp userDetails/firstName = [Thai First Name] userDetails/middleName​ = [Thai Title Name] userDetails/lastName = [Thai Last Name] userDetails/salutation​ = [English Title Name] userDetails/otherLanguageDetails/firstName​ = [English First Name] userDetails/otherLanguageDetails/middleName =​ “” userDetails/otherLanguageDetails/lastName​ = [English Last Name] Remark: If Fail to Create TSP Profile, OPO will not retry
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- [AuditLog] Step 25 - NTB Registration – Update Segment Level Response1: Success Response2: Fail
- [AuditLog] Step 26 - NTB Registration – Create TSP Profile Response1: Success Response2: Fail
- [ActivityLog] Step 27 - NTB Registration – Create TSP Profile Response1: Success (Log Level2) Response2: Fail (Log Level1)
- [AuditLog] Step 24 - NTB Registration – Get Customer Profile Response1: Success Response2: Fail
- [AuditLog] (Fail Only) Step 25 - NTB Registration – Get RM Account List Response1: Success Response2: Fail
- 11B.4 NDID RTA status ‘Approved’
- CDP3: Update Onboard success
- 10A.2 Authentication Success
- 10B.4 NDID RTA status ‘Approved’
- If “H21: Get Daily Total Limit” success, then - Use segmentLevel of max dailyTotalLimit (H21: Get Daily Total Limit) for “Update Segment Level”. Otherwise, skip “Update Segment Level”.
- [AuditLog] Step 4 - NTB Registration - Create BeMyId RTA Response1: Success Response2: Fail
- [AuditLog] Step 5 - NTB Registration – Cancel BeMyId RTA Response1: Success Response2: Fail
- [ActivityLog] Step 5 - NTB Registration – Cancel BeMyId Request Response1: Success (Log level2) Response2: Fail (Log Level1)
- [AuditLog] Step 6 - NTB Registration – Check BeMyId RTA Status Response1: Success Response2: Fail
- [ActivityLog] Step 7 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : Null NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_DipChip’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
- [AuditLog] Step 8 - NTB Registration – Get NDID TC Response1: Success Response2: Fail
- [AuditLog] Step 9 - NTB Registration – NDID TC Acceptance Response1: Success Response2: Fail
- [AuditLog] Step 10 - NTB Registration – GetIDPBankList Response1: Success Response2: Fail
- [AuditLog] Step 11 - NTB Registration – Create NDID RTA Response1: Success Response2: Fail
- [AuditLog] Step 12 - NTB Registration – Cancel NDID RTA Response1: Success Response2: Fail
- [AuditLog] Step 13 - NTB Registration – Check NDID RTA Status Response1: Success Response2: Fail
- Mapping RTA If ndid_status = ‘WFA’ or ‘WFP’ then Set RTAStatus = ‘Processing’ Else If ndid_status = ‘CMP’ and cust_action = ’accept’ then Set RTAStatus = ‘Approved’ Else If ndid_status = ‘CMP’ and cust_action = ’reject’ then Set RTAStatus = ‘Rejected’ Else If ndid_status = ‘EXP’ then Set RTAStatus = ‘Expired’ Else If ndid_status = ‘CCL’ then Set RTAStatus = ‘Cancelled’ Else If ndid_status = ‘ERR’ then Set RTAStatus = ‘Error’ Set RTAExpiryDate = input_date + request_timeout Set RTACreatedDateTime = input_date
- If RTA Status: ‘Approved’ (ndid_status=’CMP’, cust_action = ‘accept’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- [ActivityLog] Step 14 - NTB Registration – GetAuthenResult Response1: Success (Log level2) Response2: Fail (Log Level1)
- Publish Event Topic: dev.stg.efmconsumer.advice Event Type: XXXX Request: NCBD Session Correlation ID : x-transactionId CIS ID : NULL NCBD Registered E-mail : NULL NCBD Registered Phone Number : NULL NCBD User first log on : NCBD registration date in IA NCBD registration date : NCBD registration date in IA Channel - Message Type : ‘Registration’ Channel - Channel Type : x-channel Channel – SubChannel : ‘NCBD’ Channel - Server DateTime : System Datetime Authentication Method : NULL Authentication Result : 1:success Transaction Language : TH|EN Source System = ‘ApiGee’ SAS Decision Flag = 1:Need EFM decision TransactionType = ‘Authen_NDID’ TransactionSubType = ‘NTB’:transaction success | OPO Cust Error Code: transaction fail Response:
- POST MMP1 - Add Logic to handle case customer back to flow after IA fail to complete customer profile on Save state 3
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If pass face compare
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- 11B.4 NDID RTA status ‘Approved’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error
- 10A.2 Authentication Success
- 10B.4 NDID RTA status ‘Approved’
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If pass face compare
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- 10B.4 NDID RTA status ‘Approved’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and channelTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ channelTypeValue is not ‘na’ then continue to call H3: CustomerToAcctRel Inquiry - Else, Return Error
- After clicking Sign up, CIAM will check device try count - 1-10: pass - 11-20: delay 10 mins - >20: delay till the end of the day
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [CIAM Validate Condition NTB flow] 1. Not has RM 2. Validate DOB that users fill in (>= 15 years old) If pass validate, then record ID Number, Mobile No. to use for validation in screen 7 of NTB Flow and return response.
- [CIAM Validate] If pass below conditions, then can proceed further 1. ID Expiry date >= Today 2. ID Issue Date <= Today 3. Age >= 15 years If fails either 1 out of 3, shows full screen error
- [CIAM Validate] If Pass PIN policy below, then can proceed further 1. 6 Digits of number e.g. [MASKED_CODE] 2. No adjacent repeating numbers for 4-6 digits long e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE] 3. No simple sequences both ascending or descending e.g. [MASKED_CODE], [MASKED_CODE], [MASKED_CODE], [MASKED_CODE]
- ‘Verified’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate “Inprogress RTA” Status (RTA Record matched CI and ProcessInstantKey) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Registered’] or [RTAStatus = ‘Processing’] Then, proceed next step to B_CheckRTA SubFlow Else if RTAStatus = ‘Verified’, continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Processing’] Then, proceed next step to M_CheckRTA SubFlow Else if RTAStatus = ‘Approved’ then continue at Re-validate Save state and Post Authentication Else, proceed to Map Response from DB information Otherwise, proceed next step Get All RTA List (In case have no RTA Record matched CI and ProcessInstantKey)
- Re-validate Save state and Post Authentication (In case has In-progress RTA Record and RTAStatus = Verified (BeMyID) or Approved (NDID)) In case ReferenceId start with ‘B_XX’ If [RTAStatus = ‘Verified’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process In case If ReferenceId start with ‘NCBD_XX’ If [RTAStatus = ‘Approved’] and and InvalidFlag = ‘N’ If Save state = 2 then, Continue to Mapping FlowType Process Else, Record Save state = 2 for this Customer then, Continue to Mapping FlowType Process Otherwise,Continue to Proceed Mapping FlowType
- ‘Fail Post Authen’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘Y’)
- ‘Approved’ (RTAStatus = ‘Approved’ and InvalidFlag = ‘N’)
- Validate Flow Type to Display If FlowType = ’InProgressRTA’ then validate ReferenceId and RTAStatus If RerferenceId start with ‘B_XXX’ - RTAStatus = ‘Verified’ then, navigate to [10A.2] - RTAStatus = ‘Expired’ then, navigate to [10A.2] - RTAStatus = ‘Locked/Rejected’ then, navigate to [10A.2] - RTAStatus = ‘Registered’ then, navigate to [10A.1] - RTAStatus = ‘Processing’ then, navigate to [10A.1] If RerferenceId start with ‘M_XXX’ - RTAStatus = ‘Approved’ then, navigate to [10B.4] - RTAStatus = ‘Expired’ then, navigate to [10B.4] - RTAStatus = ‘Rejected’ then, navigate to [10B.4] - RTAStatus = ‘Error’ then, navigate to [10B.4] - RTAStatus = ‘Processing’ then, navigate to [10B.3] If FlowType = ‘NewRTAnoNDID’ then, navigate to [10N.1] If FlowType = ‘NewRTA’ then, then, navigate to [10N.2] If FlowType = ‘B_FailAuthen’ then, navigate to [10A.2] Screen Fail Post Authen If FlowType = ‘N_FailAuthen’ then, navigate to [10B.4] Screen Fail Post Authen
- Mapping FlowType 1. Check In Progress RTA to separate return FlowType With Latest RTA Record with same ProcessInstantKey in session In case ReferendId start with ‘B_XXX’ If RTAStatus != ‘Verified’ then, return FlowType = ‘InprogressRTA’ Else if, RTAStatus = ‘Verified’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘B_FailAuthen’ In case ReferendId start with ‘NCBD_XX’ If RTAStatus != ‘Approved’ then, return FlowType = ‘InprogressRTA’ Else if RTAStatus = ‘Approved’ If InvalidFlag = ‘N’, return FlowType = ‘InprogressRTA’ Else if InvalidFlag = ‘Y’, return FlowType = ‘N_FailAuthen’ If have no RTA record with same ProcessInstantKey, then continue to Check NDID option available 2. Check NDID option available If Count all of ReferendId start with ‘NCBD_XX’ >= 10 then, return FlowType = ‘NewRTAnoNDID’ Else, FlowType = ‘NewRTA’ Map Additional Field Response In case ReferendId start with ‘NCBD_XX’ ‘IDPBankLogoUrl’ = [Prefix URL]/IDPCompanyCode ‘WarningMessageTH’ ‘WarningMessageEN’ ‘appNameTh’ = app_name_thai from IDPWhitelist configuration ‘appNameEn’ = app_name_eng from IDPWhitelist configuration ‘RTAApprovedDateTime’ = ndid_status_date when ndid_status=”CMP” + cust_action=”Accept” ‘RTAExpiryDateTime’ In case ReferendId start with ‘B_XXX’ ‘ServicePointUrl’ = [ServicePointUrl] from Configuration ‘machineName’ ‘CustomerRefNo’ ‘RTAApprovedDateTime’ = bblOnlineDopaDateTime ‘RTAExpiryDateTime’
- If pass face compare
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/customer-profile/v2/internal/customers/inquiry", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- - Case create RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case create RM fail, CIS will return error
- [AuditLog] in case Fail/Success Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = 'Check action >> 'CREATE', - actSubType = ‘'Inquiry without JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v2/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- - Case update RM success and CIS error, CIS will return RMNO and Return CISID with null/ blank - Case update RM fail, CIS will return error
- Create CustomerProfile (With New field ‘Registration Channel’) and CIS ID, RMNO If Success, proceed next step further. Else, Return Error
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- E2: Consume Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backend API' - actSubType = 'RM Add Relationship' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "cbrm-services/customers/accounts/relationship", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = If Any - alternateIdType = RMNO - alternateId = RMNO - initiateBy = Filled by common lib - bblTraceId - actSource = 'NCCI' - actGroup = 'Internal' - actType = 'Backed API' - actSubType = 'Update PDPA' - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.desc - deviceInfo = n/a - logLevel = 2 - channel = n/a - recordedDateTime = n/a - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/PDPA/consent/update", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- E4:Publish Event topic: <env>.cis.update.customer.success Event Type: DELETE_MOBILE_NUMBER
- E5:Consume Event Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- H14: File - Batch Update RM profile (RM no., Phone number) generate from Event topic: <env>.cis.update.customer.success, Event Type: CREATE_CUSTOMER and Event topic: <env>.cis.update.customer.success, Event Type: DELETE_MOBILE_NUMBER H15: File - Batch update relationship (RM No., CIS No.) Generate from Event topic: <env>.cis.api.service.failed, EventType: FAIL_RM_CIS_ADD_REL
- Compare Segment & Daily Total Limit 1. Get daliyTotalLimit by segment (from RM) in configure D13 -> 30,000 2. Validate dailyTotalLimit If Max of dailyTotalLimit (from oCRM) >= dailyTotalLimit (from RM - H19), then set - segmentLevel = segmentLevel (from oCRM) D13, Otherwise, If get daily total limit from oCRM (H21) success, set - segmentLevel = 1st digit of segmentLevel (from oCRM) B + all digit exclude 1st digit of segmentLevel (from RM). Else, set segmentLevel = segmentLevel (from RM)
- E1:Publish Event topic: <env>.cis.create.customer.success EventType: CREATE_CUSTOMER Remark: TSP จะ Ignore error เพราะยังไม่ได้สร้าง Profile ที่ TSP เลย และต้องไม่ retry
- [AuditLog] in case Fail Only - id = Filled by common lib - schemaVersion = Filled by common lib - sourceDateTime = <system datetime> - cisId = Filled by common lib - alternateIdType = <identityType> - alternateId = <identityValue> - initiateBy = Filled by common lib - bblTraceId - actSource = Use API header (BBL-Forwarded-For-Channel) - actGroup = ‘API’ - actType = ‘Inquiry’ - actSubType = ‘'Inquiry with JWT token'’ - actStatus = [‘Success’, ‘Fail’] - errorCode = API response status.code - errorMessage = API response status.message - deviceInfo = n/a - logLevel = 2 - channel = Use API header (BBL-Channel) - recordedDateTime = DB only (Generate during DB insert) - reqPayload = Map request payload - auditData = { "apiCall": { "url": "/cis/v1/customers-accounts/inquiry/account", "httpStatus": "200", "errorResponse": { <map response of API calls, only if httpStatus is not 200> } } }
- 11B.4 NDID RTA status ‘Approved’
- [CIAM validate] Validate RM has value If, RM has no value and idType in request is ‘PP’ or ‘OI’ or ‘AI’ Then Return Error Else If, RM has no value and idType in request is ‘CI’ Then proceed next step following to NTB Flow Else if, RM has value Then check DOB - Validate dob from CIS Customer Search by Citizen ID/PP response match with DOB that customer input, If no, return error - Validate dob from CIS Customer Search by Citizen ID/PP response ,that user >= 12 years old, If no, return error If pass above dob validation then check - If CISID has value and partyBlockedStatus = ‘AC’ and partyTypeValue = ‘na’ and partyChennelStatus = ‘AC’ and partyChannelBlock = ‘N’ then Check CHANNEL_STATUS in IAM <> ‘Suspended’. If it true then, continue at Reactivate Flow Else, Return Error - Else If CISID has no value or CISID has value and partyBlockedStatus = ‘PE’ or ‘FD’ value in x-channel does not exist in channelTypeValue then continue to ETB Flow (Call to H19: BBLOwnCustCheckInq) - Else, Return Error

## Cleanup Contract

- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- H11: Close RTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- [AuditLog] in case Fail/Success Only Data Check. Delete Duplicate mobile
- E1: Publish Event Topic: <env>.raw.cis.party.update Event Type: contactnumber.delete
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- E3: Consume Event Topic: <env>.raw.cis.party.create Event Type: party.create Topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete Topic: <env>.raw.cis.party.update, Event Type: email.delete
- 1) H14: File - Batch to RM Update Mobile Number (RM no., Phone number) from Event topic: <env>.raw.cis.party.create, Event Type: party.create Event topic: <env>.raw.cis.party.update, Event Type: contactnumber.delete 2) H15: File - Batch to RM Add Relationship (RM No., CIS No.) from CIS DB Party Table 3) H16: File – Batch to ATM mgmt Pre DAF File (Account no., Account control1,2,3,4) from CIS DB PartyArrangement Table
- H11: Close RTA-NDID URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-BeMyId Otherwise, Close Pop-up and stay in the page
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = {IdNum, ChipNo, CardNo}, from Response H7 - Check Gender from Response H7 If Gender = 1, update Gender = ‘M’ to OPO DB Else if Gender = 2, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTAApprovedDateTime = bblDopaOnlineDateTime, - DOPADateTime = bblDopaOnlineDateTime, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, BirthDate_PassValidateFlag,ID_PassValidateFlag,IssueDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- H11: Close RTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
- Validate RTA Status If RTAStatus = ‘Processing’ Then, proceed to next step H11: Close RTA-NDID Else if RTAStatus = ‘Error’ or ‘Expired’ or ‘Rejected’ Then Skip H11 and proceed at Get All RTA List from OPO DB by CI Else, retrun Error
- Display Pop-Up For Asking customer to confirm to Change Authentication Method If customer Tap confirm, start call Cancel RTA-NDID Otherwise, Close Pop-up and stay in the page
- Validate Post Authentication Result If InvalidFlag = ‘N’ Then, update DB with - AS_Data = answered_as{Exclude ‘customer_biometric’}, from Response H10 - Check Gender from Response H10 If Gender = M, update Gender = ‘M’ to OPO DB Else if Gender = F, update Gender = ‘F’ to OPO DB Else, No update for Gender to OPO DB - RTA ApprovedDateTime = ndid_status_date, - UpdateDateTime, - SaveState = 2 If InvalidFlag = ‘Y’ Then Return Error and Clear Digital ID on Device Update DB with FirstNameTH_PassValidateFlag, LastNameTH_PassValidateFlag, FirstNameEN_PassValidateFlag, LastNameEN_PassValidateFlag, ID_PassValidateFlag, BirthDate_PassValidateFlag, InvalidFlag, InvalidReason, UpdateDateTime
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- H11: Close RTA-NDID [New Service] URL: POST /NDIDSwagger/RPServices/rp/request/close Request: reference_id Response: http code
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.
- OPO call delete Digital ID in user device and Direct customer to Beginning point
- Validate Save state expiry If Save state = ‘2’ and Save State Expiry Date >= Date.Now, Then proceed on next step to Call Create Customer Profile-NTB Else, return error and Call to Delete DigitalID on user device
- Note Possible Cases: - No CIS, No RM -> [CIS request to RM] for Create Customer Profile If success then, CIS create Profile and CIS ID - Has CIS, No RM -> Could not happened - No CIS, Has RM and still in progress in save stage (Save state not Expired) -> Update KYC - No CIS, Has RM with ending the flow (Save state Expired, User deleted app) -> OPO Need to Block and delete DIgitalId from device then this customer will comback to ‘ETB Flow’
- Validate Response If Has CIS ID, Then Update Save State = 3 And Call IAM to update DigitalID Profile, Add CIS ID and Clear ProcessInstantKey, Call Onboard TSP Else, Return General Error
- Delete phone number from other profile (if duplicate) -> Broadcast to other systems
- Delete duplicate mobile no.

## Canonical Components Used

- [AuditLog] in case Fail/Success Only API Inquiry with JWT token
- After customer Tap at this CTA, Continue service at Tap ‘NTB_Registration’
- After customer Tap at this CTA, Continue service at Tap ‘RTA_BeMyID’
- After customer Tap at this CTA, Continue service at Tap ‘RTA_NDID’
- Apigee (Engagement)
- Apigee (Enterprise)
- Apigee (Experience)
- Authen via KeyCloke
- B_Cancel RTA
- B_CheckRTA
- B_Re-Gen RefNo
- BLDG
- CIAM (SAAS – no SecureConnect)
- CIFS (CH24)
- CIS
- Consent Blob CMS
- Consent DB CMS
- Consent service CMS
- Create ProcessInstantKey
- CTA Scenario
- Customer Change Method (Cancel RTA)
- Customer Check RTA Status
- DOPA Gateway
- ESIS
- FARA
- Get Customer Profile from OPO DB
- Get Customer Profile Temp from OPO DB
- IAM Proxy (Experience)
- Kafka
- M_Cancel RTA
- M_CheckRTA
- N_Re-Gen RTA
- NA App
- NCBD System
- NDID Gateway
- NDID Platform
- New Entry
- OCR Server
- oCRM
- OPO (Camunda)
- OPO (camunda)
- OPO (Database)
- OPO-MS (Engagement)
- OPO-MS (Experience)
- P I N G
- PDPA
- Record #Save State 2
- REMOVE
- Retry 3 times
- RM
- SAS
- SMCS
- SMS Gateway
- ‘Expired’ RTAStatus = ‘Expired’
- ‘Rejected’ RTAStatus = ‘Rejected’
