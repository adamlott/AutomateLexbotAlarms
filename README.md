As the name indicates, this repository is code that can automate the creation of Cloudwatch Alarms for Amazon Lexbots.

An Eventbridge rule named Lexbots is monitoring Cloudtrail for a pattern that can be found in Rule-Lexbots-CloudFormation-Template.json.  When a Lexbot Alias called 'PROD' is created, the CreateParameterStoreEntriesForLexbots lambda is invoked.

Anoher Lambda called CreateCloudWatchAlarms-Lex is being invoked by an EventBridge that can be found in this rule: Rule-MonitorChangesInParameterStoreForLex-CloudFormation-Template.json. 


The QueryAllLexbots Lambda function can be used to validate the entries in Parameter Store
