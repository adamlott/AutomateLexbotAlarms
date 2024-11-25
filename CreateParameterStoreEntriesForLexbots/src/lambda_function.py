import boto3
import os

# Initialize Boto3 clients for LexV2 and SSM (Parameter Store)
lex_client = boto3.client('lexv2-models')
ssm_client = boto3.client('ssm')

def lambda_handler(event, context):
    # Get the list of Lex bots
    bots = lex_client.list_bots()
    
    for bot in bots['botSummaries']:
        bot_id = bot['botId']
        bot_name = bot['botName']
        
        # Get bot aliases for the current bot
        aliases = lex_client.list_bot_aliases(botId=bot_id)
        
        for alias in aliases['botAliasSummaries']:
            alias_name = alias['botAliasName']
            alias_id = alias['botAliasId']
            
            # Check if the alias is "PROD"
            if alias_name.upper() == 'PROD':
                # Create parameter store entries for BotAliasId and BotId
                try:
                    # Create BotAliasId parameter
                    ssm_client.put_parameter(
                        Name=f'/lex/{bot_name}/BotAliasId',
                        Value=alias_id,
                        Type='String',
                        Overwrite=True
                    )
                    print(f"Created/updated /lex/{bot_name}/BotAliasId with value {alias_id}")
                    
                    # Create BotId parameter
                    ssm_client.put_parameter(
                        Name=f'/lex/{bot_name}/BotId',
                        Value=bot_id,
                        Type='String',
                        Overwrite=True
                    )
                    print(f"Created/updated /lex/{bot_name}/BotId with value {bot_id}")
                
                except Exception as e:
                    print(f"Error creating parameters for bot: {bot_name}. Error: {e}")

    return {
        'statusCode': 200,
        'body': 'Parameter Store entries created/updated for bots with alias "PROD".'
    }
