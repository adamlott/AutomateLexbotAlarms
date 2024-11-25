import boto3

def lambda_handler(event, context):
    # Initialize the Lex client
    lex_client = boto3.client('lexv2-models')
    
    # List to hold all bot information
    bot_info = []
    
    # Pagination for list_bots
    next_token = None
    
    while True:
        # Query Lex for the list of bots, handling pagination
        if next_token:
            response = lex_client.list_bots(nextToken=next_token)
        else:
            response = lex_client.list_bots()
        
        bots = response['botSummaries']
        
        # Iterate through each bot
        for bot in bots:
            bot_name = bot['botName']
            bot_id = bot['botId']
            
            # Print BotName and BotId to the console
            print(f'BotName: {bot_name}, BotId: {bot_id}')
            
            # Base entry with BotName and BotId
            bot_data = {
                'BotName': bot_name,
                'BotId': bot_id,
                'BotAliasId': None  # Default to None if no PROD alias is found
            }
            
            # Handle pagination for list_bot_aliases
            alias_next_token = None
            
            while True:
                # Query Lex for the bot aliases, handling pagination
                if alias_next_token:
                    alias_response = lex_client.list_bot_aliases(botId=bot_id, nextToken=alias_next_token)
                else:
                    alias_response = lex_client.list_bot_aliases(botId=bot_id)
                
                aliases = alias_response['botAliasSummaries']
                
                for alias in aliases:
                    alias_name = alias['botAliasName']
                    bot_alias_id = alias['botAliasId']
                    
                    # Check if the alias name is 'PROD'
                    if alias_name == 'PROD':
                        print(f'PROD alias found for {bot_name}: {bot_alias_id}')
                        bot_data['BotAliasId'] = bot_alias_id
                        break  # Stop searching once 'PROD' alias is found
                
                # Check if there's another page of aliases
                alias_next_token = alias_response.get('nextToken')
                if not alias_next_token:
                    break
            
            # Add the bot data to the list
            bot_info.append(bot_data)
        
        # Check if there's another page of bots
        next_token = response.get('nextToken')
        if not next_token:
            break
    
    # Return bot and alias information
    return {
        'statusCode': 200,
        'body': bot_info
    }