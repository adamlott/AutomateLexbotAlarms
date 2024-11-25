import boto3
import re

# Initialize AWS clients
ssm = boto3.client('ssm')
cloudwatch = boto3.client('cloudwatch')

def get_parameters_by_path(prefix):
    """
    Fetch parameters from Parameter Store that start with a specific prefix.
    """
    parameters = []
    next_token = None
    
    while True:
        # Get parameters by path
        if next_token:
            response = ssm.get_parameters_by_path(Path=prefix, Recursive=True, NextToken=next_token)
        else:
            response = ssm.get_parameters_by_path(Path=prefix, Recursive=True)
        
        parameters.extend(response['Parameters'])
        
        # If there are more results, continue fetching
        next_token = response.get('NextToken')
        if not next_token:
            break

    return parameters

def extract_bot_name(parameter_name):
    """
    Extract bot_name from the parameter name, assuming it follows
    the pattern /lex/{bot_name}/{something_else}.
    """
    pattern = r'^/lex/([^/]+)'
    match = re.match(pattern, parameter_name)
    if match:
        bot_name = match.group(1)
        return bot_name
    return None

def get_bot_id(bot_name):
    """
    Retrieve BotId from the Parameter Store for a given bot_name.
    """
    bot_id_param_name = f'/lex/{bot_name}/BotId'
    
    try:
        response = ssm.get_parameter(Name=bot_id_param_name)
        bot_id = response['Parameter']['Value']
        return bot_id
    except ssm.exceptions.ParameterNotFound:
        print(f"BotId not found for bot: {bot_name}")
        return None

def get_bot_alias_id(bot_name):
    """
    Retrieve BotAliasId from the Parameter Store for a given bot_name.
    """
    alias_param_name = f'/lex/{bot_name}/BotAliasId'
    
    try:
        response = ssm.get_parameter(Name=alias_param_name)
        bot_alias_id = response['Parameter']['Value']
        return bot_alias_id
    except ssm.exceptions.ParameterNotFound:
        print(f"BotAliasId not found for bot: {bot_name}")
        return None

def create_cloudwatch_alarm(bot_name, bot_id, bot_alias_id):
    """
    Create a CloudWatch alarm for RuntimeSystemErrors for a given Lex bot.
    """
    alarm_name = f"AdamConnect-dev - RuntimeSystemErrors-{bot_name}"
    
    # Add debugging logs
    print(f"Creating alarm for BotName: {bot_name}, BotId: {bot_id}, BotAliasId: {bot_alias_id}")

    # Create CloudWatch alarm
    response = cloudwatch.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='RuntimeSystemErrors',
        Namespace='AWS/Lex',
        Period=300,
        Statistic='Average',
        Threshold=1.0,  # Alarm if there is more than 1 erro
        TreatMissingData='notBreaching',
        ActionsEnabled=True,
        AlarmActions=[],  # SNS Topic ARN for notifications
        AlarmDescription=f"Alarm for RuntimeSystemErrors on Lex bot {bot_name}",
        Dimensions=[
            {
                'Name': 'LocalId',
                'Value': 'en_US'
            },
            {
                'Name': 'BotId',  # Using BotId retrieved from Parameter Store
                'Value': bot_id
            },
            {
                'Name': 'Operation',
                'Value': 'StartConversation'
            },
            {
                'Name': 'BotAliasId',  # Using retrieved BotAliasId
                'Value': bot_alias_id
            },
        ],

    )
    
    return response

def lambda_handler(event, context):
    # Step 1: Get all parameters starting with /lex/
    prefix = '/lex/'
    parameters = get_parameters_by_path(prefix)
    
    # Step 2: Create a CloudWatch alarm for each Lex bot
    for parameter in parameters:
        parameter_name = parameter['Name']
        bot_name = extract_bot_name(parameter_name)
        
        # Add debugging logs
        print(f"Parameter: {parameter_name}, BotName: {bot_name}")
        
        if bot_name:
            # Retrieve BotId and BotAliasId from Parameter Store
            bot_id = get_bot_id(bot_name)
            bot_alias_id = get_bot_alias_id(bot_name)
            
            if bot_id and bot_alias_id:
                response = create_cloudwatch_alarm(bot_name, bot_id, bot_alias_id)
                print(f"Created alarm for {bot_name}: {response}")
            else:
                print(f"Skipping alarm creation for {bot_name}, as BotId or BotAliasId could not be found.")

    return {
        'statusCode': 200,
        'body': 'CloudWatch alarms created successfully.'
    }