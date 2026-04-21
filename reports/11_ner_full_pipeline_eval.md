# Report

- Generated at: 2026-04-21 10:10:29 UTC
- Model: `microsoft/deberta-v3-base (fine-tuned NER + full post-processing pipeline)`
- Test samples: 10

## Metrics

- samples: 10
- exact_match: 1.00 (100.00%)
- masking_recall: 1.00 (100.00%)
- over_masking_rate: 0.00 (0.00%)
- text_preservation: 1.00 (100.00%)

## Preview

### Sample 1

**Source Text (Input)**

```text
Hello Mrs. Walker, can you check why my recent transfer of $250 hasn't been processed? My account number is 567890 and my email is megan.walker@example.com.
```

**Model Raw Output**

```text
Hello [PREFIX], can you check why my recent transfer of [AMOUNT] hasn't been processed? My account number is [ACCOUNT_NUMBER] and my email is [EMAIL].
```

**Extracted Final Answer (Output)**

```text
Hello [PREFIX], can you check why my recent transfer of [AMOUNT] hasn't been processed? My account number is [ACCOUNT_NUMBER] and my email is [EMAIL].
```

**Reference Masked Text (Target)**

```text
Hello [PREFIX], can you check why my recent transfer of [AMOUNT] hasn't been processed? My account number is [ACCOUNT_NUMBER] and my email is [EMAIL].
```

### Sample 2

**Source Text (Input)**

```text
Dear Ms. Garcia, I need to report a lost debit card. My phone number is (555) 789-0123 and my account number is 678901.
```

**Model Raw Output**

```text
Dear [PREFIX], I need to report a lost debit card. My phone number is [PHONE_NUMBER] and my account number is [ACCOUNT_NUMBER].
```

**Extracted Final Answer (Output)**

```text
Dear [PREFIX], I need to report a lost debit card. My phone number is [PHONE_NUMBER] and my account number is [ACCOUNT_NUMBER].
```

**Reference Masked Text (Target)**

```text
Dear [PREFIX], I need to report a lost debit card. My phone number is [PHONE_NUMBER] and my account number is [ACCOUNT_NUMBER].
```

### Sample 3

**Source Text (Input)**

```text
I'd like to know if there are any charges incurred when transferring the payment to my bank account with SQVPZAP9. If yes, could you please tell me in details?
```

**Model Raw Output**

```text
I'd like to know if there are any charges incurred when transferring the payment to my bank account with [BIC]. If yes, could you please tell me in details?
```

**Extracted Final Answer (Output)**

```text
I'd like to know if there are any charges incurred when transferring the payment to my bank account with [BIC]. If yes, could you please tell me in details?
```

**Reference Masked Text (Target)**

```text
I'd like to know if there are any charges incurred when transferring the payment to my bank account with [BIC]. If yes, could you please tell me in details?
```

### Sample 4

**Source Text (Input)**

```text
Hi Mrs. Brown, I need to reset my online banking password. My username is michael.brown and my phone number is (555) 678-9101.
```

**Model Raw Output**

```text
Hi [PREFIX], I need to reset my online banking password. My username is [USERNAME] and my phone number is [PHONE_NUMBER].
```

**Extracted Final Answer (Output)**

```text
Hi [PREFIX], I need to reset my online banking password. My username is [USERNAME] and my phone number is [PHONE_NUMBER].
```

**Reference Masked Text (Target)**

```text
Hi [PREFIX], I need to reset my online banking password. My username is [USERNAME] and my phone number is [PHONE_NUMBER].
```

### Sample 5

**Source Text (Input)**

```text
"Hello, Jordane Volkman, we have detected irregular activities on our Money Market Account account number 86885470 with a transaction amount of 668.42Canadian Dollar. Can you please look into this matter and ensure that our procedures were followed correctly?"
```

**Model Raw Output**

```text
"Hello, [FIRSTNAME] [LASTNAME], we have detected irregular activities on our [ACCOUNTNAME] account number [ACCOUNT_NUMBER] with a transaction amount of [AMOUNT][CURRENCY]. Can you please look into this matter and ensure that our procedures were followed correctly?"
```

**Extracted Final Answer (Output)**

```text
"Hello, [FIRSTNAME] [LASTNAME], we have detected irregular activities on our [ACCOUNTNAME] account number [ACCOUNT_NUMBER] with a transaction amount of [AMOUNT][CURRENCY]. Can you please look into this matter and ensure that our procedures were followed correctly?"
```

**Reference Masked Text (Target)**

```text
"Hello, [FIRSTNAME] [LASTNAME], we have detected irregular activities on our [ACCOUNTNAME] account number [ACCOUNT_NUMBER] with a transaction amount of [AMOUNT][CURRENCY]. Can you please look into this matter and ensure that our procedures were followed correctly?"
```

### Sample 6

**Source Text (Input)**

```text
For your financial protection, we would like to confirm the credit card 9372417504319872 with CVV 174 is authorized for payments. A test transaction of ﷼323.04 will be processed.
```

**Model Raw Output**

```text
For your financial protection, we would like to confirm the credit card [CREDITCARDNUMBER] with CVV [CREDITCARDCVV] is authorized for payments. A test transaction of [CURRENCYSYMBOL][AMOUNT] will be processed.
```

**Extracted Final Answer (Output)**

```text
For your financial protection, we would like to confirm the credit card [CREDITCARDNUMBER] with CVV [CREDITCARDCVV] is authorized for payments. A test transaction of [CURRENCYSYMBOL][AMOUNT] will be processed.
```

**Reference Masked Text (Target)**

```text
For your financial protection, we would like to confirm the credit card [CREDITCARDNUMBER] with CVV [CREDITCARDCVV] is authorized for payments. A test transaction of [CURRENCYSYMBOL][AMOUNT] will be processed.
```

### Sample 7

**Source Text (Input)**

```text
Hi Mr. Scott, I have a question about my loan repayment. My name is Ethan Scott and my account number is 901234.
```

**Model Raw Output**

```text
Hi [PREFIX], I have a question about my loan repayment. My name is [NAME] and my account number is [ACCOUNT_NUMBER].
```

**Extracted Final Answer (Output)**

```text
Hi [PREFIX], I have a question about my loan repayment. My name is [NAME] and my account number is [ACCOUNT_NUMBER].
```

**Reference Masked Text (Target)**

```text
Hi [PREFIX], I have a question about my loan repayment. My name is [NAME] and my account number is [ACCOUNT_NUMBER].
```

### Sample 8

**Source Text (Input)**

```text
Hi Mr. Miller, I need assistance with my credit card rewards program. My username is joseph.miller and my SSN is 444-55-6666.
```

**Model Raw Output**

```text
Hi [PREFIX], I need assistance with my credit card rewards program. My username is [USERNAME] and my SSN is [SSN].
```

**Extracted Final Answer (Output)**

```text
Hi [PREFIX], I need assistance with my credit card rewards program. My username is [USERNAME] and my SSN is [SSN].
```

**Reference Masked Text (Target)**

```text
Hi [PREFIX], I need assistance with my credit card rewards program. My username is [USERNAME] and my SSN is [SSN].
```

### Sample 9

**Source Text (Input)**

```text
Hello Mr. Brown, my debit card was declined. My account number is 789012 and my phone number is (555) 678-9101.
```

**Model Raw Output**

```text
Hello [PREFIX], my debit card was declined. My account number is [ACCOUNT_NUMBER] and my phone number is [PHONE_NUMBER].
```

**Extracted Final Answer (Output)**

```text
Hello [PREFIX], my debit card was declined. My account number is [ACCOUNT_NUMBER] and my phone number is [PHONE_NUMBER].
```

**Reference Masked Text (Target)**

```text
Hello [PREFIX], my debit card was declined. My account number is [ACCOUNT_NUMBER] and my phone number is [PHONE_NUMBER].
```

### Sample 10

**Source Text (Input)**

```text
Dear Ms. Nelson, can you please update my contact number to (555) 234-5678? My account number is 789012 and my email is isabella.nelson@example.com.
```

**Model Raw Output**

```text
Dear [PREFIX], can you please update my contact number to [PHONE_NUMBER]? My account number is [ACCOUNT_NUMBER] and my email is [EMAIL].
```

**Extracted Final Answer (Output)**

```text
Dear [PREFIX], can you please update my contact number to [PHONE_NUMBER]? My account number is [ACCOUNT_NUMBER] and my email is [EMAIL].
```

**Reference Masked Text (Target)**

```text
Dear [PREFIX], can you please update my contact number to [PHONE_NUMBER]? My account number is [ACCOUNT_NUMBER] and my email is [EMAIL].
```
