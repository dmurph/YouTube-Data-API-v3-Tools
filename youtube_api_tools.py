import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import io
import os

class YouTubeAPIException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class YouTubeDataAPIv3Tools:
    """
        This is a wrapper around the YouTube v3 API.
        
        A 'client_secret.json' file is needed in order for this class to be functional.
        Or should I say ... classy ....
        
        Required Python modules:
            google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
                
        Keep in mind that you need to have the proper OAuth 2.0 authentication set up and the 
        permissions to manage playlists for an account. Below is a step-by-step guide on how to
        obtain a client_secret.json file. 
        
        Please also note that the steps for setting up OAuth 2.0 authentication and using the 
        client_secret.json file might change over time. For the latest and most detailed 
        instructions, you should refer to the official Google API documentation for the YouTube 
        API and OAuth 2.0 authentication for Python.
        
        1) Google Cloud Console:

            To use the YouTube API or any other Google API, you need to create a project on the 
            Google Cloud Console and enable the APIs you want to use.
            
        2) OAuth 2.0 Credentials:
        
            After creating the project and enabling the YouTube API, you need to create OAuth 2.0 
            credentials. These credentials are used to identify your application and to 
            authenticate and authorize access to the API. The credentials contain a client ID, 
            client secret, and other information.
                
        3) Download Client Secret:

            Once you create OAuth 2.0 credentials, you can download the client_secret.json file 
            from the Google Cloud Console. This file contains the client ID and client secret, 
            which are used in the authentication process.
            
        4) Authentication Flow:
        
            When you run your Python application that interacts with the YouTube API, it will 
            prompt the user to authenticate their Google account through a web browser (if necessary). 
            The client_secret.json file is used during this authentication flow to identify your 
            application and establish a secure connection.
            
        5) Access Tokens:

            After the user grants permission to your application, the authentication server provides 
            your application with an access token. This access token is used in API requests to 
            prove that your application has been granted permission to access the user's resources.

        6) Protecting Client Secret:
            
            The client_secret.json file contains sensitive information (client secret), so it should 
            be kept confidential and not shared or exposed publicly. It is important to store the 
            client_secret.json file securely on the server-side of your application.
            
        When you use the Google API Client Library for Python to interact with the YouTube API, you'll 
        need to set up the OAuth 2.0 authentication flow and provide the path to the client_secret.json 
        file in your code to initiate the authentication process.
        
    """
    def __init__(
        self, 
        _client_secrets_json_path: str,
        _scopes: list, 
        _token_file: str="token.pickle",
        _dev_key: str=None, 
        _channel_id: str=None
    ) -> None:
        
        """
            Initializes the YouTubeAPIClient object.
        """

        self.api_scopes = []

        if _scopes is not None:
            for i in range(len(_scopes)):
                self.api_scopes.append(_scopes[i])
        
        self.CLIENT_SECRETS_JSON_FILE = _client_secrets_json_path
        self.DEV_KEY = _dev_key
        self.CHANNEL_ID = _channel_id
        
        if _channel_id is not None:
            self.CHANNEL_ID = _channel_id
        
        self.api_obj = {
            "scopes": self.api_scopes,
            "json": self.CLIENT_SECRETS_JSON_FILE
        }
        
        self.TOKEN_FILE = _token_file
        
        self.service = self.get_authenticated_service()
    
    #////// UTILITY METHODS //////
    
    def _dict_to_arr(self, dictionary: dict):
        if isinstance(dictionary, dict):
            array = []
            for key in dictionary.keys():
                array.append(dictionary[key])
            return array
            
    def add_scope(self, scope: str) -> (list | None):
        """
        Adds the given scope to the list of scopes held in the api_scopes list.
        Returns the new list of scopes if successful and None otherwise. 
        """
        try:
            for i in range(len(self.api_scopes)):
                if self.api_scopes[i] == scope:
                    return None
                else:
                    self.api_scopes.append(scope)
                    return self.api_scopes
        except IndexError as ie:
            print(f"Index Error.\n{ie}")
            return None
        except TypeError as te:
            print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
            return None
        
    def add_scopes(self, scopes: list[str]) -> (list | None): 
        """
        Adds one or more API scopes to the list of scopes.
        returns the new list if successful and None otherwise.
        """
        try:
            for i in range(len(scopes)):
                self.api_scopes.append(scopes[i])
            return self.api_scopes
        except IndexError as ie:
            print(f"Index Error.\n{ie}")
            return None
        except TypeError as te:
            print(f"Type error: You may have forgotten to enclose the list of scopes with square brackets [scope1, scope2, ...] !\n{te}")
            return None
            
    def remove_scope(self, scope: str) -> (list | None):
        """
        Removes the given scope from the list of scopes being used and
        returns the new list. Returns None otherwise.
        """
        try:
            for _scope in range(len(self.api_scopes)):
                if self.api_scopes[_scope] == scope:
                    self.api_scopes.pop(_scope)
                    return self.api_scopes
        except IndexError as ie:
            print(f"Index Error.\n{ie}")
            return None
        except TypeError as te:
            print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
            return None
      
    def remove_scopes(self, scopes: list) -> (list | None):
        """
        Removes one or more scopes from the list of scopes being used and
        returns the new list. Returns None otherwise.
        """
        try:
            for i in range(len(scopes)):
                for j in range(len(self.api_scopes)):
                    if self.api_scopes[j] == scopes[i]:
                        self.api_scopes.pop(j)
            return self.api_scopes
        except IndexError as ie:
            print(f"Index Error.\n{ie}")
            return None
        except TypeError as te:
            print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
            return None
    
    def set_client_secrets_json(self, client_secrets_json: str) -> bool:
        """
        Sets the path to the client_secrets.json file. Returns True if file 
        passed has is the correct file type and False otherwise.
        """
        if client_secrets_json.endswith(".json"):
            self.CLIENT_SECRETS_JSON_FILE = client_secrets_json
            return True
        return False    
    
    def get_client_secrets_json(self) -> (str | None):
        """
        Returns the path to the client_secrets.json file or None if no file is stored.
        """
        if len(self.CLIENT_SECRETS_JSON_FILE) != 0:
            return self.CLIENT_SECRETS_JSON_FILE
        return None
    
    
    #//////////// AUTHENTICATION ////////////
    
    def _get_authenticated_service(self, credentials) -> object:
        """
        This method is a wrapper around the 'googleapiclient.discovery.build' method.
        It returns the resource needed for interacting with the YouTube API.
        """
        _credentials = credentials
        return googleapiclient.discovery.build(
            "youtube", 
            "v3", 
            credentials=_credentials,
            developerKey=self.DEV_KEY
        )

    def get_authenticated_service(self) -> (object | None):
        """
        When you call get_authenticated_service(), it will initiate the OAuth 2.0 authentication 
        flow, prompting the user to grant access to your application to the specified 
        scopes (in this case, "https://www.googleapis.com/auth/youtube.readonly"). Once 
        the user grants permission, the credentials will be stored in a local file named 
        "token.pickle" for future use. Subsequent calls to get_authenticated_service() will 
        load the credentials from the file without re-authentication.
        """
        # Note to self: Think about making 'flow' & 'credentials' available as 
        # class variables instead of a local variable so that this specific 
        # instance can be accessed outside of get_authenticated_service.
        import pickle
        credentials = None
        try:
            # Check if credentials are stored in a local file (to avoid re-authentication)
            if os.path.exists(self.TOKEN_FILE):
                with open(self.TOKEN_FILE, "rb") as token_file:
                    credentials = pickle.load(token_file)

            # If no credentials found, perform the OAuth 2.0 flow
            if not credentials or not credentials.valid:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_JSON_FILE, self.api_scopes)
                credentials = flow.run_local_server(port=0)
            
                with open(self.TOKEN_FILE, "wb") as token_file:
                    pickle.dump(credentials, token_file)
            youtube_service = self._get_authenticated_service(credentials)
            return youtube_service
        except googleapiclient.errors.HttpError as e:
            print(f"An API error occurred: {e}")
            return None
            
    #//////////// CHANNEL ////////////
    class Channel:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        #////// UTILITY METHODS //////
        def get_channel_numbers(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets channel statistics for either your channel or a channel 
            specified by channel_id. Returns a dictionary containing the channels 
            view count, subscriber count and video count if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    request = service.channels().list(
                        part="snippet,statistics",
                        id=channel_id
                    )
                    response = request.execute()
                    if "items" in response:
                        channel = response["items"][0]
                        numbers = {
                            "viewCount": channel['statistics']['viewCount'],
                            "videoCount": channel['statistics']['videoCount'],
                            "subscriberCount": channel['statistics']['subscriberCount'] 
                        }
                        return numbers
                    else:
                        None
                else:
                    request = service.channels().list(
                        part="snippet,statistics",
                        mine=your_channel
                    )
                    response = request.execute()
                    if "items" in response:
                        channel = response["items"][0]
                        numbers = {
                            "viewCount": channel['statistics']['viewCount'],
                            "videoCount": channel['statistics']['videoCount'],
                            "subscriberCount": channel['statistics']['subscriberCount'] 
                        }
                        return numbers
                    else:
                        None
                    
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// ENTIRE CHANNEL RESOURCE //////
        def get_channel(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the resource json for either your channel or a channel specified by 
            channel_id. Returns the entire Channel resource as a dictionary if successful 
            and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        channel = channel["items"][0]
                        return channel
                    else:
                        return None
                else:
                    channel = service.channels().list(
                            part="snippet",
                            mine=your_channel
                        ).execute()
                    if "items" in channel:
                        channel = channel["items"][0]
                        return channel
                    else:
                        return None
                    
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no channels with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// CHANNEL KIND //////
        def get_channel_kind(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the kind of channel for either your channel or a channel specified 
            by channel_id. Returns the kind of channel if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        kind = channel["items"][0]["kind"]
                        return kind
                    else:
                        return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        kind = channel["items"][0]["kind"]
                        return kind
                    else:
                        return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no channels with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
    
        #////// CHANNEL ETAG //////
        def get_etag(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the etag for either your channel or a channel specified by channel_id.
            Returns the etag of the channel if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        etag = channel["items"][0]["etag"]
                        return etag
                    else:
                        return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        etag = channel["items"][0]["etag"]
                        return etag
                    else:
                        return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no channels with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// CHANNEL ID //////
        def get_id(self, your_channel: bool=True, channel_name: str=None) -> (str | None):
            """
            Gets the ID for either your channel or a channel specified by channel_name.
            This method returns the channel ID if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="id",
                        forUsername=channel_name
                    ).execute()
                    if "items" in channel:
                        id = channel["items"][0]["id"]
                        return id
                    else:
                        return None
                else:
                    channel = service.channels().list(
                        part="id",
                        mine=True
                    ).execute()
                    if "items" in channel:
                        id = channel["items"][0]["id"]
                        return id
                    else:
                        return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"No channel ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL SNIPPET //////
        def get_snippet(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the snippet part for either your channel or a channel specified by channel_id.
            Returns the snippet part of the channel resource json if successful and
            None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        snippet = channel["items"][0]["snippet"]
                        return snippet
                    else:
                        return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        snippet = channel["items"][0]["snippet"]
                        return snippet
                    else:
                        return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL TITLE //////
        def get_channel_name(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the title for either your channel or a channel specified by channel_id.
            Returns the channel title if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["snippet"]["title"]
                        return title
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["snippet"]["title"]
                        return title
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def set_channel_name(self, new_name: str, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Sets the title of either your channel or the channel specified by channel_id.
            Returns True if it was set successfully and False otherwise.
            """
            service = self.service

            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        snippet = channel["items"][0]["snippet"]
                        snippet["title"] = new_name

                        service.channels().update(
                            part="snippet",
                            body={
                                "id": channel_id,
                                "snippet": snippet
                            }
                        ).execute()
                        return True
                    else: return False
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        snippet = channel["items"][0]["snippet"]
                        snippet["title"] = new_name

                        service.channels().update(
                            part="snippet",
                            body={
                                "id": channel_id,
                                "snippet": snippet
                            }
                        ).execute()
                        return True
                    else: return False
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL DESCRIPTION //////
        def get_description(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the description for either your channel or a channel specified by 
            channel_id.
            Returns the channel description if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        desc = channel["items"][0]["snippet"]["description"]
                        return desc
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        desc = channel["items"][0]["snippet"]["description"]
                        return desc
                    else: return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def set_description(self, new_description: str, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Sets the channel description of the channel specified by channel_id.
            Returns True if it was set successfully and False otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        snippet = channel["items"][0]["snippet"]
                        snippet["description"] = new_description

                        service.channels().update(
                            part="snippet",
                            body={
                                "id": channel_id,
                                "snippet": snippet
                            }
                        ).execute()
                        return True
                    else: return False
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        snippet = channel["items"][0]["snippet"]
                        snippet["description"] = new_description

                        service.channels().update(
                            part="snippet",
                            body={
                                "id": channel_id,
                                "snippet": snippet
                            }
                        ).execute()
                        return True
                    else: return False
                    

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL CUSTOM URL //////
        def get_custom_url(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the custom URL for either your channel or a channel specified by 
            channel_id.
            Returns the channels custom URL if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["customUrl"]
                        return url
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["customUrl"]
                        return url
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL PUBLISHED DATE //////
        def get_time_published_at(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the datetime either your channel or a channel specified by channel_id was
            published at.
            Returns the datetime the channel was published at if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        date = channel["items"][0]["snippet"]["publishedAt"]
                        return date
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        date = channel["items"][0]["snippet"]["publishedAt"]
                        return date
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL THUMBNAILS //////
        def get_thumbnails(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the thumbnails for either your channel or a channel specified by channel_id.
            Returns a dictionary containing the thumbnails if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnails = channel["items"][0]["snippet"]["thumbnails"]
                        return thumbnails
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnails = channel["items"][0]["snippet"]["thumbnails"]
                        return thumbnails
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
           
        #////// CHANNEL DEFAULT RES THUMBNAIL //////
        def get_default_res_thumbnail(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Get the default res thumbnail for either your channel or a channel specified by channel_id.
            Returns a dictionary containing the default thumbnail if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["default"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["default"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_default_res_thumbnail_url(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Get thedefault res thumbnail URL for either your channel or a channel specified by channel_id.
            Returns the default res thumbnail URL if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["thumbnails"]["default"]["url"]
                        return url
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["thumbnails"]["default"]["url"]
                        return url
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_default_res_thumbnail_width(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the default res thumbnail width for either your channel or a channel specified 
            by channel_id.
            Returns the default thumbnail width if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["default"]["width"]
                        return int(width)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["default"]["width"]
                        return int(width)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_default_res_thumbnail_height(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the default res thumbnail height for either your channel or a channel specified 
            by channel_id.
            Returns the default thumbnail height if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["default"]["height"]
                        return int(height)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["default"]["height"]
                        return int(height)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// CHANNEL MEDIUM RES THUMBNAIL //////
        def get_medium_res_thumbnail(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the medium res thumbnail for either your channel or a channel specified by 
            channel_id.
            Returns a dictionary containing the medium res thumbnail if successful and None 
            otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["medium"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["medium"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_medium_res_thumbnail_url(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the medium res thumbnail URL for either your channel or a channel specified 
            by channel_id.
            Returns the medium res thumbnail URL if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
                        return url
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
                        return url
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_medium_res_thumbnail_width(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets a the medium res thumbnail width for either your channel or a channel specified 
            by channel_id.
            Returns the medium res thumbnail width if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["medium"]["width"]
                        return int(width)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["medium"]["width"]
                        return int(width)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_medium_res_thumbnail_height(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the medium res thumbnail height for either your channel or a channel specified 
            by channel_id.
            Returns the medium res thumbnail height if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["medium"]["height"]
                        return int(height)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["medium"]["height"]
                        return int(height)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// CHANNEL HIGH RES THUMBNAIL //////
        def get_high_res_thumbnail(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the high res thumbnail for either your channel or a channel specified 
            by channel_id.
            Returns a dictionary containing the high res thumbnail if successful and None 
            otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["high"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["high"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_high_res_thumbnail_url(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the high res thumbnail URL for either your channel or a channel specified 
            by channel_id.
            Returns the high res thumbnail URL if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                        return url
                    return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        url = channel["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                        return url
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_high_res_thumbnail_width(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the high res thumbnail width for either your channel or a channel specified 
            by channel_id.
            Returns the high res thumbnail width if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["high"]["width"]
                        return int(width)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["high"]["width"]
                        return int(width)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_high_res_thumbnail_height(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the high res thumbnail height for either your channel or a channel specified 
            by channel_id.
            Returns the high res thumbnail height if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["high"]["height"]
                        return int(height)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["high"]["height"]
                        return int(height)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// CHANNEL STANDARD RES THUMBNAIL //////
        def get_standard_res_thumbnail(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the standard res thumbnail for either your channel or a channel specified 
            by channel_id.
            Returns a dictionary containing the standard res thumbnail if successful and None 
            otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.videos().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["standard"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.videos().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["standard"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_standard_res_thumbnail_url(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the standard res thumbnail URL for either your channel or a channel specified 
            by channel_id.
            Returns the standard res thumbnail URL if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["standard"]["url"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["standard"]["url"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_standard_res_thumbnail_width(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the standard res thumbnail width for either your channel or a channel specified 
            by channel_id.
            Returns the standard res thumbnail width if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["standard"]["width"]
                        return int(width)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["standard"]["width"]
                        return int(width)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_standard_res_thumbnail_height(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the standard res thumbnail height for either your channel or a channel specified 
            by channel_id.
            Returns the standard res thumbnail height if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["standard"]["height"]
                        return int(height)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["standard"]["height"]
                        return int(height)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        #////// CHANNEL MAX RES THUMBNAIL //////
        def get_max_res_thumbnail(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the max res thumbnail for either your channel or a channel specified by channel_id.
            Returns a dictionary containing the max res thumbnail if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["maxres"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["maxres"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_max_res_thumbnail_url(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the max res thumbnail URL for either your channel or a channel specified 
            by channel_id.
            Returns the max res thumbnail URL if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
                        return thumbnail
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        thumbnail = channel["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
                        return thumbnail
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_max_res_thumbnail_width(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the max res thumbnail width for either your channel or a channel specified 
            by channel_id.
            Returns the max res thumbnail width if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["maxres"]["width"]
                        return int(width)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        width = channel["items"][0]["snippet"]["thumbnails"]["maxres"]["width"]
                        return int(width)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_max_res_thumbnail_height(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets teh max res thumbnail height for either your channel or a channel specified 
            by channel_id.
            Returns the max res thumbnail height if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["maxres"]["height"]
                        return int(height)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        height = channel["items"][0]["snippet"]["thumbnails"]["maxres"]["height"]
                        return int(height)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
                
        #////// CHANNEL DEFAULT LANGUAGE //////
        def get_default_language(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the default language for either your channel or a channel specified 
            by channel_id.
            Returns the default language if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        lang = channel["items"][0]["snippet"]["defaultLanguage"]
                        return lang
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        lang = channel["items"][0]["snippet"]["defaultLanguage"]
                        return lang
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL LOCALIZED DATA //////
        def get_localized_data(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the localized data for either your channel or a channel specified by channel_id.
            Returns the localized data in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        data = channel["items"][0]["snippet"]["localized"]
                        return data
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        data = channel["items"][0]["snippet"]["localized"]
                        return data
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL LOCALIZED TITLE //////
        def get_localized_title(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the localized title for either your channel or a channel specified by channel_id.
            Returns the localized title if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["snippet"]["localized"]["title"]
                        return title
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["snippet"]["localized"]["title"]
                        return title
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL LOCALIZED DESCRIPTION //////
        def get_localized_description(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the localized description for either your channel or a channel specified by channel_id.
            Returns the localized description if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        description = channel["items"][0]["snippet"]["localized"]["description"]
                        return description
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        description = channel["items"][0]["snippet"]["localized"]["description"]
                        return description
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL COUNTRY //////
        def get_origin_country(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the country for either your channel or a channel specified by channel_id.
            Returns the country code if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="snippet",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        country = channel["items"][0]["snippet"]["country"]
                        return country
                    else: return None
                else:
                    channel = service.channels().list(
                        part="snippet",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        country = channel["items"][0]["snippet"]["country"]
                        return country
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL CONTENT DETAILS //////
        def get_content_details(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the content details for either your channel or a channel specified by channel_id.
            Returns the content details part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["contentDetails"]
                        return details
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["contentDetails"]
                        return details
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL RELATED PLAYLISTS //////
        def get_related_playlists(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the related playlists for either your channel or a channel specified by channel_id.
            Returns the playlists if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        playlists = channel["items"][0]["contentDetails"]["relatedPlaylists"]
                        return playlists
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        playlists = channel["items"][0]["contentDetails"]["relatedPlaylists"]
                        return playlists
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL LIKES //////
        def get_likes(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the likes for either your channel or a channel specified by channel_id.
            Returns the likes if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        likes = channel["items"][0]["contentDetails"]["relatedPlaylists"]["likes"]
                        return likes
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        likes = channel["items"][0]["contentDetails"]["relatedPlaylists"]["likes"]
                        return likes
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL FAVORITES //////
        def get_favorites(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the favorites for either your channel or a channel specified by channel_id.
            Returns the favorites if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        favs = channel["items"][0]["contentDetails"]["relatedPlaylists"]["favorites"]
                        return favs
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        favs = channel["items"][0]["contentDetails"]["relatedPlaylists"]["favorites"]
                        return favs
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL UPLOADS //////
        def get_uploads(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the uploads for either your channel or a channel specified by channel_id.
            Returns the uploads if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        uploads = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                        return uploads
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        uploads = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                        return uploads
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL STATISTICS //////
        def get_statistics(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the statistics for either your channel or a channel specified by channel_id.
            Returns the statistics part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="statistics",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        statistics = channel["items"][0]["statistics"]
                        return statistics
                    else: return None
                else:
                    channel = service.channels().list(
                        part="statistics",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        statistics = channel["items"][0]["statistics"]
                        return statistics
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL VIEW COUNT //////
        def get_view_count(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the view count for either your channel or a channel specified by channel_id.
            Returns the count if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="statistics",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        count = channel["items"][0]["statistics"]["viewCount"]
                        return int(count)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="statistics",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        count = channel["items"][0]["statistics"]["viewCount"]
                        return int(count)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL SUBSCRIBER COUNT //////
        def get_subscriber_count(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the subscriber count for either your channel or a channel specified by channel_id.
            Returns the count if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="statistics",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        count = channel["items"][0]["statistics"]["subscriberCount"]
                        return int(count)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="statistics",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        count = channel["items"][0]["statistics"]["subscriberCount"]
                        return int(count)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL HIDDEN SUBSCRIBER COUNT //////
        def has_hidden_subscriber_count(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Returns True if either your channel or a channel specified by channel_id has a 
            hidden subscriber count and False otherwise. Returns None if field doesn't exist
            and upon error.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="statistics",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        has = channel["items"][0]["statistics"]["hidenSubscriberCount"]
                        return bool(has)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="statistics",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        has = channel["items"][0]["statistics"]["hidenSubscriberCount"]
                        return bool(has)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL VIDEO COUNT //////
        def get_video_count(self, your_channel: bool=True, channel_id: str=None) -> (int | None):
            """
            Gets the video count for either your channel or a channel specified by channel_id.
            Returns the count if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="statistics",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        count = channel["items"][0]["statistics"]["videoCount"]
                        return int(count)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="statistics",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        count = channel["items"][0]["statistics"]["videoCount"]
                        return int(count)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL TOPIC DETAILS //////
        def get_topic_details(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the topic details for either your channel or a channel specified by channel_id.
            Returns the topic details part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="topicDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["topicDetails"]
                        return details
                    else: return None
                else:
                    channel = service.channels().list(
                        part="topicDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["topicDetails"]
                        return details
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL TOPIC IDS //////
        def get_topic_ids(self, your_channel: bool=True, channel_id: str=None) -> (list[str] | None):
            """
            Gets the topic IDs for either your channel or a channel specified by channel_id.
            Returns the IDs in a list if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="topicDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        ids = channel["items"][0]["topicDetails"]["topicIds"]
                        return ids
                    else: return None
                else:
                    channel = service.channels().list(
                        part="topicDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        ids = channel["items"][0]["topicDetails"]["topicIds"]
                        return ids
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL TOPIC CATEGORIES //////
        def get_topic_categories(self, your_channel: bool=True, channel_id: str=None) -> (list[str] | None):
            """
            Gets the topic categories for either your channel or a channel specified by channel_id.
            Returns the categories in a list if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="topicDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        cats = channel["items"][0]["topicDetails"]["topicCategories"]
                        return cats
                    else: return None
                else:
                    channel = service.channels().list(
                        part="topicDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        cats = channel["items"][0]["topicDetails"]["topicCategories"]
                        return cats
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL STATUS //////
        def get_status(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the status part for either your channel or a channel specified by channel_id.
            Returns the status part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="status",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        status = channel["items"][0]["status"]
                        return status
                    else: return None
                else:
                    channel = service.channels().list(
                        part="status",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        status = channel["items"][0]["status"]
                        return status
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL PRIVACY STATUS //////
        def get_privacy_status(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the privacy status for either your channel or a channel specified by channel_id.
            Returns the status if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="status",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        status = channel["items"][0]["status"]["privacyStatus"]
                        return status
                    else: return None
                else: 
                    channel = service.channels().list(
                        part="status",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        status = channel["items"][0]["status"]["privacyStatus"]
                        return status
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL IS LINKED //////
        def is_linked(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Returns True if either your channel or a channel specified by channel_id is 
            linked and False otherwise. Returns None if field doesn't exist
            and upon error.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="status",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        linked = channel["items"][0]["status"]["isLinked"]
                        return bool(linked) 
                    else:
                        return None
                else:
                    channel = service.channels().list(
                        part="status",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        linked = channel["items"][0]["status"]["isLinked"]
                        return bool(linked) 
                    else:
                        return None 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL LONG UPLOADS STATUS //////
        def get_long_uploads_status(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the long upload status for either your channel or a channel specified by channel_id.
            Returns the status if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="status",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        status = channel["items"][0]["status"]["longUploadsStatus"]
                        return status
                    else: return None
                else:
                    channel = service.channels().list(
                        part="status",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        status = channel["items"][0]["status"]["longUploadsStatus"]
                        return status
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL MADE FOR KIDS //////
        def is_made_for_kids(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Returns True if either your channel or a channel specified by channel_id is 
            made for kids and False otherwise. Returns None if field doesn't exist
            and upon error.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="status",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        kids = channel["items"][0]["status"]["madeForKids"]
                        return bool(kids) 
                    else:
                        return None
                else:
                    channel = service.channels().list(
                        part="status",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        kids = channel["items"][0]["status"]["madeForKids"]
                        return bool(kids) 
                    else:
                        return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL SELF DECLARED MADE FOR KIDS //////
        def is_self_declared_made_for_kids(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Returns True if either your channel or a channel specified by channel_id is self 
            declared made for kids and False otherwise. Returns None if field doesn't exist
            and upon error.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="status",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        kids = channel["items"][0]["status"]["selfDeclaredMadeForKids"]
                        return bool(kids) 
                    else: return None
                else:
                    channel = service.channels().list(
                        part="status",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        kids = channel["items"][0]["status"]["selfDeclaredMadeForKids"]
                        return bool(kids) 
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL BRANDING SETTINGS //////
        def get_branding_settings(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the branding settings for either your channel or a channel specified by channel_id.
            Returns the settings part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        settings = channel["items"][0]["brandingSettings"]
                        return settings
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        settings = channel["items"][0]["brandingSettings"]
                        return settings
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL BRANDING //////
        def get_branding(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the branding for either your channel or a channel specified by channel_id.
            Returns the branding part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        branding = channel["items"][0]["brandingSettings"]["channel"]
                        return branding
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        branding = channel["items"][0]["brandingSettings"]["channel"]
                        return branding
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL BRAND TITLE //////
        def get_brand_name(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the channel brand title for either your channel or a channel specified by channel_id.
            Returns the title if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["brandingSettings"]["channel"]["title"]
                        return title
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["brandingSettings"]["channel"]["title"]
                        return title
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL BRAND DESCRIPTION //////
        def get_brand_description(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the channel brand description for either your channel or a channel specified by channel_id.
            Returns the description if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        description = channel["items"][0]["brandingSettings"]["channel"]["description"]
                        return description
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        description = channel["items"][0]["brandingSettings"]["channel"]["description"]
                        return description
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL KEYWORDS //////
        def get_channel_hashtags(self, your_channel: bool=True, channel_id: str=None) -> (list[str] | None):
            """
            Gets the keywrds for either your channel or a channel specified by channel_id.
            Returns the keywords in a list if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        keywords = channel["items"][0]["brandingSettings"]["channel"]["keywords"]
                        return keywords
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        keywords = channel["items"][0]["brandingSettings"]["channel"]["keywords"]
                        return keywords
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL TRACKING ANALYTICS ACCOUNT ID //////
        def get_tracking_analytics_account_id(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the tracking analytics account ID for either your channel or a channel 
            specified by channel_id.
            Returns the ID if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        id = channel["items"][0]["brandingSettings"]["channel"]["trackingAnalyticsAccountId"]
                        return id
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        id = channel["items"][0]["brandingSettings"]["channel"]["trackingAnalyticsAccountId"]
                        return id
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL HAS MODERATE COMMENTS //////
        def has_moderate_comments(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Returns True if either your channel or the channel specified by channel_id has 
            moderate comments and False otherwise. Returns None upon error.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        moderate = channel["items"][0]["brandingSettings"]["channel"]["moderateComments"]
                        return bool(moderate)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        moderate = channel["items"][0]["brandingSettings"]["channel"]["moderateComments"]
                        return bool(moderate)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL UNSUBSCRIBED TRAILER //////
        def get_unsubscribed_trailer(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the unsubscribed trailer for either your channel or a channel specified by channel_id.
            Returns the trailer if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        trailer = channel["items"][0]["brandingSettings"]["channel"]["unsubscribedTrailer"]
                        return trailer
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        trailer = channel["items"][0]["brandingSettings"]["channel"]["unsubscribedTrailer"]
                        return trailer
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL BRAND DEFAULT LANGUAGE //////
        def get_brand_default_language(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the channel brands default language for either your channel or a channel specified by channel_id.
            Returns the default lnguage if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        lang = channel["items"][0]["brandingSettings"]["channel"]["defaultLanguage"]
                        return lang
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        lang = channel["items"][0]["brandingSettings"]["channel"]["defaultLanguage"]
                        return lang
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL BRAND COUNTRY //////
        def get_brand_origin_country(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the channel brands country for either your channel or a channel specified by channel_id.
            Returns the country if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        country = channel["items"][0]["brandingSettings"]["channel"]["country"]
                        return country
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        country = channel["items"][0]["brandingSettings"]["channel"]["country"]
                        return country
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL WATCH DATA //////
        def get_watch_data(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the channel watch data for either your channel or a channel specified by channel_id.
            Returns the channel watch data part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        watch = channel["items"][0]["brandingSettings"]["watch"]
                        return watch
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        watch = channel["items"][0]["brandingSettings"]["watch"]
                        return watch
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL WATCH TEXT COLOR //////
        def get_watch_text_color(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the watch text color for either your channel or a channel specified by channel_id.
            Returns the watch text color if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        color = channel["items"][0]["brandingSettings"]["watch"]["textColor"]
                        return color
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        color = channel["items"][0]["brandingSettings"]["watch"]["textColor"]
                        return color
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL WATCH BACKGROUND COLOR //////
        def get_watch_background_color(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the watch background color for either your channel or a channel specified by channel_id.
            Returns the watch background color if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:    
                        color = channel["items"][0]["brandingSettings"]["watch"]["backgroundColor"]
                        return color
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:    
                        color = channel["items"][0]["brandingSettings"]["watch"]["backgroundColor"]
                        return color
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL FEATURED PLAYLIST ID //////
        def get_featured_playlist_id(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the featured playlist ID for either your channel or a channel specified by channel_id.
            Returns the featured playlist ID if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="brandingSettings",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        id = channel["items"][0]["brandingSettings"]["watch"]["featuredPlaylistId"]
                        return id
                    else: return None
                else:
                    channel = service.channels().list(
                        part="brandingSettings",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        id = channel["items"][0]["brandingSettings"]["watch"]["featuredPlaylistId"]
                        return id
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL AUDIT DETAILS //////
        def get_audit_details(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the audit details for either your channel or a channel specified by channel_id.
            Returns the audit details part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="auditDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["auditDetails"]
                        return details
                    else: return None
                else:
                    channel = service.channels().list(
                        part="auditDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["auditDetails"]
                        return details
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL OVERALL GOOD STANDING //////
        def has_overall_good_standing(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Checks if either your channel or a channel specified by channel_id is in overall
            good standing.
            Returns True if so and False otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="auditDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        standing = channel["items"][0]["auditDetails"]["overallGoodStanding"]
                        return bool(standing)
                    else: return None
                else:
                    channel = service.channels().list(
                        part="auditDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        standing = channel["items"][0]["auditDetails"]["overallGoodStanding"]
                        return bool(standing)
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL COMMUNITY GUIDELINES GOOD STANDING //////
        def has_community_guidelines_good_standing(self, your_channel: bool=True, channel_id: str=None) -> (bool | None):
            """
            Checks if either your channel or a channel specified by channel_id is in good standing
            with the community guidelines.
            Returns True if so and False otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="auditDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        standing = channel["items"][0]["auditDetails"]["communityGuideLinesGoodStanding"]
                        return bool(standing)
                    else: return None
                else: 
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["contentOwnerDetails"]
                        return details
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL CONTENT OWNER DETAILS //////
        def get_content_owner_details(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the content owner details for either your channel or a channel specified by channel_id.
            Returns the content owner details part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["contentOwnerDetails"]
                        return details
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        details = channel["items"][0]["contentOwnerDetails"]
                        return details
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL CONTENT OWNER //////
        def get_content_owner(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the content owner for either your channel or a channel specified by channel_id.
            Returns the content owner if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        owner = channel["items"][0]["contentOwnerDetails"]["contentOwner"]
                        return owner
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        owner = channel["items"][0]["contentOwnerDetails"]["contentOwner"]
                        return owner
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL TIME LINKED //////
        def get_time_linked(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the time a channel was linked for either your channel or a channel specified by channel_id.
            Returns the time linked if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        time = channel["items"][0]["contentOwnerDetails"]["timeLinked"]
                        return time
                    else: return None
                else:
                    channel = service.channels().list(
                        part="contentOwnerDetails",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        time = channel["items"][0]["contentOwnerDetails"]["timeLinked"]
                        return time
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL LOCALIZATIONS //////
        def get_localizations_data(self, your_channel: bool=True, channel_id: str=None) -> (dict | None):
            """
            Gets the localizations data for either your channel or a channel specified by channel_id.
            Returns the localizations data part in a dictionary if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="localizations",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        data = channel["items"][0]["localizations"]
                        return data
                    else: return None
                else:
                    channel = service.channels().list(
                        part="localizations",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        data = channel["items"][0]["localizations"]
                        return data
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL LOCALIZATIONS TITLE //////
        def get_localizations_title(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the localizations title for either your channel or a channel specified by channel_id.
            Returns the localizations title if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="localizations",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["localizations"]["title"]
                        return title
                    else: return None
                else:
                    channel = service.channels().list(
                        part="localizations",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        title = channel["items"][0]["localizations"]["title"]
                        return title
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL LOCALIZATIONS DESCRIPTION //////
        def get_localizations_description(self, your_channel: bool=True, channel_id: str=None) -> (str | None):
            """
            Gets the localiztions description for either your channel or a channel specified by channel_id.
            Returns the localiztions description if successful and None otherwise.
            """
            service = self.service
            try:
                if not your_channel:
                    channel = service.channels().list(
                        part="localizations",
                        id=channel_id
                    ).execute()
                    if "items" in channel:
                        description = channel["items"][0]["localizations"]["description"]
                        return description
                    else: return None
                else:
                    channel = service.channels().list(
                        part="localizations",
                        mine=your_channel
                    ).execute()
                    if "items" in channel:
                        description = channel["items"][0]["localizations"]["description"]
                        return description
                    else: return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
                
    #//////////// CHANNEL BANNER ////////////
    class ChannelBanner:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        #////// UTILITY METHODS //////
        def set_channel_banner(self, channel_id: str, banner_image_url: str) -> (bool | None):
            """
            Sets the channel banner of the channel specified by channel_id.
            Returns True if successful and None otherwise.
            """
            service = self.service
            try:
                service.channels().update(
                    part="brandingSettings",
                    body={
                        "id": channel_id,
                        "brandingSettings": {
                            "image": {
                                "bannerExternalUrl": banner_image_url
                            }
                        }
                    }
                ).execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: No channel banner or no channel with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_channel_banner_default_url(self) -> (str | None):
            """
            Gets the default channel banner URL of the channel specified by channel_id.
            Returns the URL if successful and None otherwise.
            """
            service = self.service
            try:
                request = service.channelBanners().insert(
                    part="brandingSettings"
                )
                response = request.execute()
                banner_url = response.get("brandingSettings", {}).get("image", {}).get("bannerImageUrl")
                return banner_url
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: No channel banner or no channel with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def delete_channel_banner(self, channel_id) -> (bool | None):
            """
            Removes the channel banner of the channel specified by channel_id.
            Returns True if successful and None otherwise.
            """
            service = self.service
            try:
                service.channels().update(
                    part="brandingSettings",
                    body={
                        "id": channel_id,
                        "brandingSettings": {
                            "image": {
                                "bannerExternalUrl": ""
                            }
                        }
                    }
                ).execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: No channel banner or no channel with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// ENTIRE CHANNEL BANNER RESOURCE //////
        def get_channel_banner(self) -> (dict | None):
            """
            Returns the entire ChannelBanner resource as a dictionary if successful
            and None otherwise.
            """
            service = self.service
            try:
                request = service.channelBanners().insert()
                response = request.execute()
                banner = response
                return banner

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: No channel banner or no channel with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// ENTIRE CHANNEL BANNER KIND //////
        def get_channel_banner_kind(self) -> (str | None):
            service = self.service
            try:
                request = service.channelBanners().insert()
                response = request.execute()
                kind = response["kind"]
                return kind

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channel banners.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// ENTIRE CHANNEL BANNER ETAG //////
        def get_channel_banner_etag(self) -> (str | None):
            service = self.service
            try:
                request = service.channelBanners().insert()
                response = request.execute()
                etag = response["etag"]
                return etag

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channel banners.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// ENTIRE CHANNEL BANNER URL //////
        def get_channel_banner_url(self) -> (str | None):
            service = self.service
            try:
                request = service.channelBanners().insert()
                response = request.execute()
                url = response["url"]
                return url

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channel banners.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
    #//////////// CHANNEL SECTION ////////////
    class ChannelSection:
        """
        Channel sections in the context of the YouTube Data API represent different 
        types of content sections that you can organize on your YouTube channel. 
        Each section type serves a specific purpose and allows you to feature different 
        types of content prominently on your channel's front page. These are some 
        common channel section types:
        
            - AllPlaylists: Displays a collection of playlists from the channel.
            - CompletedEvents: Displays live event broadcasts that have ended.
            - LikedPlaylists: Displays playlists that the channel has liked.
            - Likes: Displays videos that the channel has liked.
            - LiveEvents: Displays upcoming and live events.
            - MultipleChannels: Displays other channels that the channel features.
            - PopularUploads: Displays the channel's most popular uploads.
            - RecentUploads: Displays the channel's most recent uploads.
            - SinglePlaylist: Displays a single playlist from the channel.
            - SubscribedChannels: Displays channels that the channel is subscribed to.
            - Uploads: Displays the channel's uploaded videos.
        """
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        #////// UTILITY METHODS //////
        def iterate_channel_sections(self, channel_id: str, func: object) -> (list[str] | None):
            service = self.service
            try:
                request = service.channelSections().list(
                    part="snippet",
                    channelId=channel_id
                )
                response = request.execute()

                for item in response["items"]:
                    func(item)
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no channels with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CHANNEL SECTION //////
        def get_channel_section(self, section_id) -> (dict | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                channel = channel["items"][0]
                return channel

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_channel_sections(self, channel_id: str) -> (dict | None):
            service = self.service
            try:
                channel = service.channelSections().list(
                    part="snippet",
                    channelId=channel_id
                ).execute()
                sections = []
                for i in range(len(channel["items"])):
                    section = channel["items"][i]
                    sections.append(section)
                return sections
            
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL SECTION KIND //////
        def get_channel_section_kind(self, section_id) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                kind = channel["items"][0]["kind"]
                return kind

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL SECTION ETAG //////
        def get_channel_section_etag(self, section_id) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                etag = channel["items"][0]["etag"]
                return etag

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL SECTION ID //////
        def get_channel_section_id_by_index(self, channel_id: str, section_index) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="id",
                    channelId=channel_id
                ).execute()

                id = channel["items"][section_index]["id"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_channel_section_id_by_type(self, channel_id: str, section_type: str) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    channelId=channel_id
                ).execute()
                for i in range(len(channel["items"])):
                    if section_type == channel["items"][i]["snippet"]["type"]:
                        id = channel["items"][i]["id"]
                        return id
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_channel_section_ids(self, channel_id: str) -> (list[str] | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="id",
                    channelId=channel_id
                ).execute()
                ids = []
                for i in range(len(channel["items"])):
                    id = channel["items"][i]["id"]
                    ids.append(id)
                return ids
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL SECTION SNIPPET //////
        def get_channel_section_snippet(self, section_id) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                snippet = channel["items"][0]["snippet"]
                return snippet

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// CHANNEL SECTION TYPE //////
        def get_channel_section_type(self, section_id) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                type = channel["items"][0]["snippet"]["type"]
                return type

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL SECTION CHANNEL ID //////
        def get_section_channel_id(self, section_id) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                id = channel["items"][0]["snippet"]["channelId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL SECTION TITLE //////
        def get_channel_section_title(self, section_id) -> (str | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                title = channel["items"][0]["snippet"]["title"]
                return title

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL SECTION POSITION //////
        def get_channel_section_position(self, section_id) -> (int | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="snippet",
                    id=section_id
                ).execute()

                position = channel["items"][0]["snippet"]["position"]
                return int(position)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL SECTION CONTENT DETAILS //////
        def get_channel_section_content_details(self, section_id) -> (dict | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="contentDetails",
                    id=section_id
                ).execute()

                details = channel["items"][0]["contentDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// CHANNEL SECTION PLAYLISTS //////
        def get_channel_section_playlists(self, section_id) -> (list[str] | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="contentDetails",
                    id=section_id
                ).execute()

                playlists = channel["items"][0]["contentDetails"]["playlists"]
                return playlists

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CHANNEL SECTION CHANNELS //////
        def get_channel_section_channels(self, section_id) -> (list[str] | None):
            service = self.service

            try:
                channel = service.channelSections().list(
                    part="contentDetails",
                    id=section_id
                ).execute()

                channels = channel["items"][0]["contentDetails"]["channels"]
                return channels

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

    #//////////// PLAYLIST ////////////
    class Playlist: 
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service

        #////// PLAYLIST UTILITIES //////
        def create_playlist(self, title: str, description: str, privacy_status: str="public") -> (dict | None):
            service = self.service
            try:
                request = service.playlists().insert(
                    part="snippet,status",
                    body={
                        "snippet": {
                            "title": title,
                            "description": description
                        },
                        "status": {
                            "privacyStatus": privacy_status
                        }
                    }
                )
                response = request.execute()
                new_playlist = {
                    "title": response['snippet']['title'],
                    "id": response['id']
                }
                return new_playlist
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
                
        def delete_playlist(self, playlist_id: str) -> bool:
            """
            With this method, you can provide the playlist_id of the playlist 
            you want to delete, and it will be removed from your YouTube account.
            """
            service = self.service
            try:
                service.playlists().delete(
                    id=playlist_id
                ).execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def save_playlist(self, source_playlist_id: str, destination_playlist_id: str) -> bool:
            """
            Save a playlist using the source and destination playlists IDs. 
            """
            try:
                videos = self.get_videos_in_playlist(source_playlist_id)
                for video in videos:
                    self.save_video_to_playlist(destination_playlist_id, video["video_id"])
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        def update_playlist_details(self, playlist_id, new_title: str=None, new_description: str=None) -> bool:
            """
            This method allows you to update the title and description of a 
            playlist with the specified playlist_id.
            """
            service = self.service

            try:
                playlist = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                ).execute()

                snippet = playlist["items"][0]["snippet"]
                if new_title:
                    snippet["title"] = new_title
                if new_description:
                    snippet["description"] = new_description

                service.playlists().update(
                    part="snippet",
                    body={
                        "id": playlist_id,
                        "snippet": snippet
                    }
                ).execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def reorder_videos(self, playlist_id: str, video_ids: list) -> bool:
            """
            This method allows you to reorder videos in a playlist by providing 
            a list of video_ids. The videos in the playlist will be reordered based 
            on the order of the provided video_ids
            """
            service = self.service
            try:
                playlist_items = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=len(video_ids)
                ).execute()

                video_positions = {}
                for item in playlist_items["items"]:
                    video_positions[item["snippet"]["resourceId"]["videoId"]] = item["snippet"]["position"]
                for video_id in video_ids:
                    position = video_positions.get(video_id, 0)
                    request = service.playlistItems().update(
                        part="snippet",
                        body={
                            "id": f"{playlist_id}_{video_id}",
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id
                                },
                                "position": position
                            }
                        }
                    )
                    request.execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def search_playlists(self, query: str, max_results: int=10) -> (list[dict] | None):
            """
            Returns a list of result snippets that matched the query.
            """
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="playlist",
                    maxResults=max_results
                )
                response = request.execute()
                result_snippets = []
                for item in response["items"]:
                    result_snippets.append(item["snippet"])
                return result_snippets
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_videos(self, playlist_id, max_results=10) -> (list | None):
            """
            This method differs from the get_videos_in_playlist method because it
            returns a list of playlist video resources for a given playlist rather than
            just the IDs and titles or just the snippet section. 
            Returns None if unsuccessful.
            """
            service = self.service
            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=max_results
                )
                response = request.execute()
                videos = []
                for video in response["items"]:
                    videos.append(video)
                return videos

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        def get_playlist_video_identities(self, playlist_id: str, max_results: int=50) -> (list | None):
            service = self.service
            try:
                videos = []
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=int(max_results)
                )
                while request is not None:
                    response = request.execute()
                    for item in response.get("items", []):
                        video_id = item["snippet"]["resourceId"]["videoId"]
                        video_title = item["snippet"]["title"]
                        videos.append({
                            "video_id": video_id,
                            "video_title": video_title
                        })
                        

                    request = service.playlistItems().list_next(request, response)
                return videos
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
            """
            This method allows you to add a video with the specified video_id 
            to a playlist with the specified playlist_id.
            """
            service = self.service
            try:
                request = service.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                )
                response = request.execute()
                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def remove_video_from_playlist(self, playlist_item_id: str) -> bool:
            """
            This method allows you to remove a video from a playlist using the 
            playlist_item_id. Note that you need to retrieve the playlist_item_id 
            of the specific video in the playlist before using this method.
            """
            service = self.service

            try:
                service.playlistItems().delete(
                    id=playlist_item_id
                ).execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def iterate_videos_in_playlist(self, playlist_id: str, func=None) -> (bool | None):
            try:
                if func is not None:
                    videos = self.get_playlist_videos(playlist_id)
                    if videos:
                        for video in videos:
                            func(video)
                        return True
                    else:
                        print(f"Unable to fetch videos in playlist with ID {playlist_id}.")
                        return False
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
             
        #////// ENTIRE PLAYLIST RESOURCE //////
        def get_playlist(self, playlist_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlists(self, max_results: int=10) -> (list | None):
            service = self.service
            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                
                playlists = []
                for playlist in response["items"]:
                    playlists.append(playlist)
                return playlists
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_liked_videos_playlist(self) -> (dict | None):

            service = self.service

            try:
                liked_playlist = None
                request = service.playlists().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                for item in response.get("items", []):
                    if item["snippet"]["title"] == "Liked videos":
                        liked_playlist = item
                        return liked_playlist
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST KIND //////
        def get_playlist_kind(self, playlist_id: str) -> (str | None):
            """
            Get the kind of playlist that the playlist is tagged as.
            """ 
            service = self.service
            try:
                request = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                )
                response = request.execute()
                playlist_kind = response['kind']
                return playlist_kind
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        def get_all_playlist_kinds(self, max_results=10) -> (list | None):
            
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                kinds = []
                for playlist in response["items"]:
                    kinds.append(playlist["kind"])
                return kinds
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// PLAYLIST ETAG //////
        def get_playlist_etag(self, playlist_id: str) -> (str | None):
            """
            Get the etag for the playlist specified by playlist_id.
            """ 
            service = self.service
            try:
                request = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                )
                response = request.execute()
                playlist_kind = response['kind']
                return playlist_kind
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_etags(self, max_results=10) -> (list | None): 
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                etags = []
                print(response['items'])
                for playlist in response["items"]:
                    etags.append(playlist["etag"])
                return etags
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ID //////    
        def get_playlist_id(self, playlist_title: str, channel_id: str=None, max_results: int=1) -> (str | None):
            service = self.service
            try:
                request = service.search().list(
                    part="id",
                    channelId=channel_id,
                    maxResults=max_results,
                    q=playlist_title,
                    type="playlist"
                )
                response = request.execute()

                if response.get("items"):
                    playlist_id = response["items"][0]["id"]["playlistId"]
                    return playlist_id

                return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_ids(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                ids = []
                for playlist in response["items"]:
                    ids.append(playlist["id"])
                return ids
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST SNIPPET //////
        def get_playlist_snippet(self, playlist_id: str) -> (str | None):
            """
            Get a playlists snippet using the playlist id.
            """
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["snippet"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_snippets(self, max_results: int=10):
    
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                snippets = []
                for playlist in response["items"]:
                    snippets.append(playlist["snippet"])
                return snippets
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// PLAYLIST PUBLISHED DATETIME //////
        def get_date_playlist_published(self, playlist_id: str) -> (str | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["publishedAt"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_published_dates(self, max_results: int=20) -> (str | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                published_dates = []
                for playlist in response["items"]:
                    published_dates.append(playlist["snippet"]["publishedAt"])
                return published_dates
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// PLAYLIST CHANNEL ID //////
        def get_playlists_channel_id(self, playlist_id: str):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info is not None:
                    return playlist_info["channelId"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// PLAYLIST TITLE //////                
        def get_playlist_title(self, playlist_id: str) -> (str | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["title"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_titles(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                titles = []
                for playlist in response["items"]:
                    titles.append(playlist["snippet"]["title"])
                return titles
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def set_playlist_title(self, playlist_id, new_title=None) -> bool:
            service = self.service

            try:
                playlist = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                ).execute()

                snippet = playlist["items"][0]["snippet"]
                if new_title:
                    snippet["title"] = new_title

                service.playlists().update(
                    part="snippet",
                    body={
                        "id": playlist_id,
                        "snippet": snippet
                    }
                ).execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// PLAYLIST DESCRIPTION //////
        def get_playlist_description(self, playlist_id: str) -> (str | None):
            """
            Get the description of a playlist using the playlist ID.
            """
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["description"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_descriptions(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                descriptions = []
                for playlist in response["items"]:
                    descriptions.append(playlist["snippet"]["description"])
                return descriptions
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def set_playlist_description(self, playlist_id, new_description: str=None) -> bool:
            
            service = self.service

            try:
                playlist = service.playlists().list(
                    part="snippet",
                    id=playlist_id
                ).execute()

                snippet = playlist["items"][0]["snippet"]
                if new_description:
                    snippet["description"] = new_description

                service.playlists().update(
                    part="snippet",
                    body={
                        "id": playlist_id,
                        "snippet": snippet
                    }
                ).execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST THUMBNAIL //////
        def get_playlist_thumbnails(self, playlist_id: str) -> (str | None):
            try: 
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_thumbnails(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// PLAYLIST DEFAULT RES THUMBNAIL //////
        def get_playlist_default_res_thumbnail(self, playlist_id: str) -> (dict | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["default"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_default_res_thumbnails(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["default"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_default_res_thumbnail_url(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["default"]["url"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_default_res_thumbnail_urls(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["default"]["url"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_default_res_thumbnail_width(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["default"]["width"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_default_res_thumbnail_height(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["default"]["height"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// PLAYLIST MEDIUM RES THUMBNAIL //////
        def get_playlist_medium_res_thumbnail(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["medium"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_medium_res_thumbnails(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["medium"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_medium_res_thumbnail_url(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["medium"]["url"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_medium_res_thumbnail_urls(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["medium"]["url"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_medium_res_thumbnail_width(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["medium"]["width"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_medium_res_thumbnail_height(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["medium"]["height"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST HIGH RES THUMBNAIL //////
        def get_playlist_high_res_thumbnail(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["high"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_high_res_thumbnails(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["high"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_high_res_thumbnail_url(self, playlist_id: str) -> (dict | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["high"]["url"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_high_res_thumbnail_urls(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["high"]["url"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_high_res_thumbnail_width(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["high"]["width"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_high_res_thumbnail_height(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["high"]["height"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST STANDARD THUMBNAIL //////
        def get_playlist_standard_res_thumbnail(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["standard"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_standard_res_thumbnails(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["standard"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_standard_res_thumbnail_url(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["standard"]["url"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_standard_res_thumbnail_urls(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["standard"]["url"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_standard_res_thumbnail_width(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["standard"]["width"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_standard_res_thumbnail_height(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["standard"]["height"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST MAX RES THUMBNAIL //////
        def get_playlist_max_res_thumbnail(self, playlist_id: str) -> (dict | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["maxres"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_max_res_thumbnails(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["maxres"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_max_res_thumbnail_url(self, playlist_id: str) -> (dict | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["thumbnails"]["maxres"]["url"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_max_res_thumbnail_urls(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                thumbnails = []
                for playlist in response["items"]:
                    thumbnails.append(playlist["snippet"]["thumbnails"]["maxres"]["url"])
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_max_res_thumbnail_width(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["maxres"]["width"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_max_res_thumbnail_height(self, playlist_id: str) -> (int | None):

            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return int(playlist_info["thumbnails"]["maxres"]["height"])
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST CHANNEL TITLE //////
        def get_playlist_channel_title(self, playlist_id: str) -> (str | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["channelTitle"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_channel_titles(self, max_results=10) -> (list | None):
            """
            I don't know why you would need to do this since this method
            will return a list of the same title due to all playlists being
            in the same channel, but I figured what the hell. Why not?
            Who knows what someone may be coding or need, so here it is 
            anyway.
            """
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                titles = []
                for playlist in response["items"]:
                    titles.append(playlist["snippet"]["title"])
                return titles
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST DEFAULT LANGUAGE //////
        def get_playlist_default_language(self, playlist_id: str) -> (str | None):
            playlist_info = self.get_playlist_snippet(playlist_id)
            if playlist_info:
                try:
                    return playlist_info['defaultLanguage']
                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"There are no playlists with the given ID.\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None
            return None

        def get_all_playlist_default_languages(self, max_results=10) -> (list | None):

            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                langs = []
                for playlist in response["items"]:
                    langs.append(playlist["snippet"]["defaultLanguage"])
                return langs
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST LOCALIZED DATA //////
        def get_playlist_localized_data(self, playlist_id: str) -> (str | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["localized"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        def get_all_playlists_localized_data(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                titles = []
                for playlist in response["items"]:
                    titles.append(playlist["snippet"]["localized"])
                return titles
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST LOCALIZED TITLE //////
        def get_playlist_localized_title(self, playlist_id: str) -> (str | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["localized"]["title"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlists_localized_titles(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                titles = []
                for playlist in response["items"]:
                    titles.append(playlist["snippet"]["localized"]["title"])
                return titles
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST LOCALIZED DESCRIPTION //////
        def get_playlist_localized_description(self, playlist_id: str) -> (str | None):
            try:
                playlist_info = self.get_playlist_snippet(playlist_id)
                if playlist_info:
                    return playlist_info["localized"]["description"]
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlists_localized_descriptions(self, max_results=10) -> (list | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                descriptions = []
                for playlist in response["items"]:
                    descriptions.append(playlist["snippet"]["localized"]["description"])
                return descriptions
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST STATUS //////
        def get_playlist_status(self, playlist_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="status",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["status"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_statuses(self, max_results: int=10):
            service = self.service

            try:
                request = service.playlists().list(
                    part="status",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                snippets = []
                for playlist in response["items"]:
                    snippets.append(playlist["status"])
                return snippets
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
       
        #////// PLAYLIST PRIVACY STATUS //////
        def get_playlist_privacy_status(self, playlist_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="status",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["status"]["privacyStatus"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except KeyError as ke:
                print(f"Key error: No privacy status field available.\n {ke}")
                return None

        def get_all_playlist_priacy_statuses(self, max_results: int=10):
            service = self.service

            try:
                request = service.playlists().list(
                    part="status",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                snippets = []
                for playlist in response["items"]:
                    snippets.append(playlist["status"]["privacyStatus"])
                return snippets
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
                return None
            except KeyError as ke:
                print(f"Key error: No privacy status field available.\n {ke}")
                return None
        
        def set_playlist_privacy_status(self, playlist_id, privacy_status):
        
            service = self.service

            try:
                playlist = service.playlists().list(
                    part="status",
                    id=playlist_id
                ).execute()

                status = playlist["items"][0]["status"]
                status["privacyStatus"] = privacy_status

                service.playlists().update(
                    part="status",
                    body={
                        "id": playlist_id,
                        "status": status
                    }
                ).execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
                return False
        
        #////// PLAYLIST CONTENT DETAILS //////
        def get_playlist_content_details(self, playlist_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="contentDetails",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["contentDetails"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except KeyError as ke:
                print(f"Key error: No content details field available.\n {ke}")
                return None

        def get_all_playlist_content_details(self, max_results: int=10): 
            service = self.service

            try:
                request = service.playlists().list(
                    part="contentDetails",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                details = []
                for playlist in response["items"]:
                    details.append(playlist["contentDetails"])
                return details
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
       
        #////// PLAYLIST ITEM COUNT //////
        def get_playlist_item_count(self, playlist_id: str) -> (int | None):

            service = self.service

            try:
                request = service.playlists().list(
                    part="contentDetails",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["contentDetails"]["itemCount"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_item_counts(self, max_results: int=10) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="contentDetails",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                counts = []
                for playlist in response["items"]:
                    counts.append(playlist["contentDetails"]["itemCount"])
                return counts
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST PLAYER //////
        def get_playlist_player(self, playlist_id: str) -> (str | None):
          
            service = self.service

            try:
                request = service.playlists().list(
                    part="player",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["player"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_players(self, max_results: int=10):
            service = self.service

            try:
                request = service.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                details = []
                for playlist in response["items"]:
                    details.append(playlist["contentDetails"])
                return details
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
       
        #////// PLAYLIST EMBED HTML //////
        def get_playlist_embed_html(self, playlist_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="player",
                    id=playlist_id
                )
                response = request.execute()

                playlist_snippet_info = response["items"][0]["player"]["embedHtml"]
                return playlist_snippet_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_embed_htmls(self, max_results: int=10) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlists().list(
                    part="player",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                counts = []
                for playlist in response["items"]:
                    counts.append(playlist["player"]["embedHtml"])
                return counts
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
    #//////////// PLAYLIST ITEM ////////////
    class PlaylistItem:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        #////// ENTIRE PLAYLIST ITEM RESOURCE //////
        def get_playlist_item_by_index(self, playlist_id: str, index: int=0) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()

                playlist_item = response["items"][index]
                return playlist_item

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_item_by_id(self, item_id: str=None) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                playlist_item = response["items"][0]
                return playlist_item

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist item with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_items(self, playlist_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                items = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    items.append(pitem)
                return items

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_playlist_item(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                playlist_item = response["items"]
                return playlist_item

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// PLAYLIST ITEM KIND //////
        def get_playlist_item_kind(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                kind = response["items"][0]["kind"]
                return kind

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_all_playlist_item_kinds(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                kinds = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    kinds.append(pitem["kind"])
                return kinds

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM ETAG //////
        def get_playlist_item_etag(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                etag = response["items"][0]["etag"]
                return etag

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_etags(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                etags = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    etags.append(pitem["etag"])
                return etags
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM ETAG //////
        def get_playlist_item_id(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["id"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_ids(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                etags = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    id.append(pitem["id"])
                return id
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM SNIPPETS //////
        def get_playlist_item_snippet(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                snippet = response["items"][0]["snippet"]
                return snippet

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_snippets(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                snippets = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    snippets.append(pitem["snippet"])
                return snippets
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM PUBLISH DATES //////
        def get_playlist_item_published_date(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                date = response["items"][0]["snippet"]["publishedAt"]
                return date

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_publish_dates(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                dates = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    dates.append(pitem["snippet"]["publishedAt"])
                return dates
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM CHANNEL ID //////
        def get_playlist_item_channel_id(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["snippet"]["channelId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_channel_ids(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                ids = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    ids.append(pitem["snippet"]["channelId"])
                return ids
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM TITLE //////
        def get_playlist_item_title(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                title = response["items"][0]["snippet"]["title"]
                return title

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_titles(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                titles = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    titles.append(pitem["snippet"]["title"])
                return titles
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM DESCRIPTION //////
        def get_playlist_item_description(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                description = response["items"][0]["snippet"]["description"]
                return description

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_descriptions(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                descriptions = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    descriptions.append(pitem["snippet"]["description"])
                return descriptions
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM THUMBNAILS //////
        def get_playlist_item_thumbnail(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                thumb = response["items"][0]["snippet"]["thumbnails"]
                return thumb

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_thumbnails(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                thumbs = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    thumbs.append(pitem["snippet"]["thumbnails"])
                return thumbs
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM DEFAULT RES THUMBNAIL //////
        def get_playlist_item_default_res_thumbnail(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                thumb = response["items"][0]["snippet"]["thumbnails"]["default"]
                return thumb

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_default_res_thumbnails(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                thumbs = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    thumbs.append(pitem["snippet"]["thumbnails"]["default"])
                return thumbs
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_default_res_thumbnail_url(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                url = response["items"][0]["snippet"]["thumbnails"]["default"]["url"]
                return url

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_default_res_thumbnail_urls(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                urls = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    urls.append(pitem["snippet"]["thumbnails"]["default"]["url"])
                return urls
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_default_res_thumbnail_width(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                width = response["items"][0]["snippet"]["thumbnails"]["default"]["width"]
                return int(width)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_default_res_thumbnail_widths(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                widths = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    widths.append(pitem["snippet"]["thumbnails"]["default"]["width"])
                return widths
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_default_res_thumbnail_height(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                height = response["items"][0]["snippet"]["thumbnails"]["default"]["height"]
                return int(height)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_default_res_thumbnail_heights(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                heights = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    heights.append(pitem["snippet"]["thumbnails"]["default"]["height"])
                return heights
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM MEDIUM RES THUMBNAIL //////
        def get_playlist_item_medium_res_thumbnail(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                thumb = response["items"][0]["snippet"]["thumbnails"]["medium"]
                return thumb

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_medium_res_thumbnails(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                thumbs = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    thumbs.append(pitem["snippet"]["thumbnails"]["medium"])
                return thumbs
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_medium_res_thumbnail_url(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                url = response["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
                return url

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_medium_res_thumbnail_urls(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                urls = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    urls.append(pitem["snippet"]["thumbnails"]["medium"]["url"])
                return urls
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_medium_res_thumbnail_width(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                width = response["items"][0]["snippet"]["thumbnails"]["medium"]["width"]
                return int(width)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_medium_res_thumbnail_widths(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                widths = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    widths.append(pitem["snippet"]["thumbnails"]["medium"]["width"])
                return widths
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_medium_res_thumbnail_height(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                height = response["items"][0]["snippet"]["thumbnails"]["medium"]["height"]
                return int(height)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_medium_res_thumbnail_heights(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                heights = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    heights.append(pitem["snippet"]["thumbnails"]["medium"]["height"])
                return heights
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM HIGH RES THUMBNAIL //////
        def get_playlist_item_high_res_thumbnail(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                thumb = response["items"][0]["snippet"]["thumbnails"]["high"]
                return thumb

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_high_res_thumbnails(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                thumbs = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    thumbs.append(pitem["snippet"]["thumbnails"]["high"])
                return thumbs
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_high_res_thumbnail_url(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                url = response["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                return url

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_high_res_thumbnail_urls(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                urls = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    urls.append(pitem["snippet"]["thumbnails"]["high"]["url"])
                return urls
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_high_res_thumbnail_width(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                width = response["items"][0]["snippet"]["thumbnails"]["high"]["width"]
                return int(width)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_high_res_thumbnail_widths(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                widths = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    widths.append(pitem["snippet"]["thumbnails"]["high"]["width"])
                return widths
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_high_res_thumbnail_height(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                height = response["items"][0]["snippet"]["thumbnails"]["high"]["height"]
                return int(height)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_high_res_thumbnail_heights(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                heights = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    heights.append(pitem["snippet"]["thumbnails"]["high"]["height"])
                return heights
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM STANDARD RES THUMBNAIL //////
        def get_playlist_item_standard_res_thumbnail(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                thumb = response["items"][0]["snippet"]["thumbnails"]["standard"]
                return thumb

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_standard_res_thumbnails(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                thumbs = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    thumbs.append(pitem["snippet"]["thumbnails"]["standard"])
                return thumbs
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_standard_res_thumbnail_url(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                url = response["items"][0]["snippet"]["thumbnails"]["standard"]["url"]
                return url

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_standard_res_thumbnail_urls(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                urls = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    urls.append(pitem["snippet"]["thumbnails"]["standard"]["url"])
                return urls
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_standard_res_thumbnail_width(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                width = response["items"][0]["snippet"]["thumbnails"]["standard"]["width"]
                return int(width)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_standard_res_thumbnail_widths(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                widths = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    widths.append(pitem["snippet"]["thumbnails"]["standard"]["width"])
                return widths
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_standard_res_thumbnail_height(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                height = response["items"][0]["snippet"]["thumbnails"]["standard"]["height"]
                return int(height)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_standard_res_thumbnail_heights(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                heights = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    heights.append(pitem["snippet"]["thumbnails"]["standard"]["height"])
                return heights
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM MAX RES THUMBNAIL //////
        def get_playlist_item_max_res_thumbnail(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                thumb = response["items"][0]["snippet"]["thumbnails"]["maxres"]
                return thumb

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_max_res_thumbnails(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                thumbs = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    thumbs.append(pitem["snippet"]["thumbnails"]["maxres"])
                return thumbs
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
                   
        def get_playlist_item_max_res_thumbnail_url(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                url = response["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
                return url

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_max_res_thumbnail_urls(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                urls = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    urls.append(pitem["snippet"]["thumbnails"]["maxres"]["url"])
                return urls
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
             
        def get_playlist_item_max_res_thumbnail_width(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                width = response["items"][0]["snippet"]["thumbnails"]["maxres"]["width"]
                return int(width)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_max_res_thumbnail_widths(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                widths = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    widths.append(pitem["snippet"]["thumbnails"]["maxres"]["width"])
                return widths
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_playlist_item_max_res_thumbnail_height(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                height = response["items"][0]["snippet"]["thumbnails"]["maxres"]["height"]
                return int(height)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_max_res_thumbnail_heights(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                heights = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    heights.append(pitem["snippet"]["thumbnails"]["maxres"]["height"])
                return heights
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM CHANNEL TITLE //////
        def get_playlist_item_channel_title(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                title = response["items"][0]["snippet"]["channelTitle"]
                return title

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_channel_titles(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                titles = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    titles.append(pitem["snippet"]["channelTitle"])
                return titles
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM VIDEO OWNER CHANNEL TITLE //////
        def get_playlist_item_video_owner_channel_title(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                title = response["items"][0]["snippet"]["videoOwnerChannelTitle"]
                return title

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_video_owner_channel_titles(self, playlist_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                titles = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    titles.append(pitem["snippet"]["videoOwnerChannelTitle"])
                return titles
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM VIDEO OWNER CHANNEL ID //////
        def get_playlist_item_video_owner_channel_id(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["snippet"]["videoOwnerChannelId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_video_owner_channel_ids(self, playlist_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                ids = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    ids.append(pitem["snippet"]["videoOwnerChannelId"])
                return ids
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM PLAYLIST ID //////
        def get_playlist_item_playlist_id(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["snippet"]["playlistId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM POSITION //////
        def get_playlist_item_position(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                position = response["items"][0]["snippet"]["position"]
                return int(position)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_positions(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                positions = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    positions.append(pitem["snippet"]["position"])
                return positions
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// PLAYLIST ITEM RESOURCE ID //////
        def get_playlist_item_resource_id(self, item_id: str) -> (int | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["snippet"]["resourceId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_resource_ids(self, playlist_id: str) -> (list[int] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                ids = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    ids.append(pitem["snippet"]["resourceId"])
                return ids
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM RESOURCE ID KIND //////
        def get_playlist_item_resource_id_kind(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                kind = response["items"][0]["snippet"]["resourceId"]["kind"]
                return kind

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_resource_id_kinds(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                kinds = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    kinds.append(pitem["snippet"]["resourceId"]["kind"])
                return kinds
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM RESOURCE ID VIDEO ID //////
        def get_playlist_item_resource_id_video_id(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["snippet"]["resourceId"]["videoId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_resource_id_video_ids(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id
                )
                response = request.execute()
                ids = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    ids.append(pitem["snippet"]["resourceId"]["videoId"])
                return ids
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM CONTENT DETAILS //////
        def get_playlist_item_content_details(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    id=item_id
                )
                response = request.execute()

                details = response["items"][0]["contentDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_items_content_details(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id
                )
                response = request.execute()
                ids = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    ids.append(pitem["contentDetails"])
                return ids
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM VIDEO ID //////
        def get_playlist_item_video_id(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    id=item_id
                )
                response = request.execute()

                id = response["items"][0]["contentDetails"]["videoId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_video_ids(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id
                )
                response = request.execute()
                ids = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    ids.append(pitem["contentDetails"]["videoId"])
                return ids
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM START AT //////
        def get_playlist_item_start_at_time(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    id=item_id
                )
                response = request.execute()

                time = response["items"][0]["contentDetails"]["startAt"]
                return time

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_start_at_times(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id
                )
                response = request.execute()
                times = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    times.append(pitem["contentDetails"]["startAt"])
                return times
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM END AT //////
        def get_playlist_item_end_at_time(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    id=item_id
                )
                response = request.execute()

                time = response["items"][0]["contentDetails"]["endAt"]
                return time

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_end_at_times(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id
                )
                response = request.execute()
                times = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    times.append(pitem["contentDetails"]["endAt"])
                return times
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM _NOTE //////
        def get_playlist_item_note(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    id=item_id
                )
                response = request.execute()

                note = response["items"][0]["contentDetails"]["note"]
                return note

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_notes(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id
                )
                response = request.execute()
                notes = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    notes.append(pitem["contentDetails"]["note"])
                return notes
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM VIDEO PUBLISHED DATE //////
        def get_playlist_item_video_published_date(self, item_id: str) -> (str | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    id=item_id
                )
                response = request.execute()

                date = response["items"][0]["contentDetails"]["videoPublishedAt"]
                return date

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_video_published_dates(self, playlist_id: str) -> (list[str] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="contentDetails",
                    playlistId=playlist_id
                )
                response = request.execute()
                dates = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    dates.append(pitem["contentDetails"]["videoPublishedAt"])
                return dates
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM STATUS //////
        def get_playlist_item_status(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="status",
                    id=item_id
                )
                response = request.execute()

                status = response["items"][0]["status"]
                return status

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_statuses(self, playlist_id: str) -> (list[dict] | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="status",
                    playlistId=playlist_id
                )
                response = request.execute()
                statuses = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    statuses.append(pitem["status"])
                return statuses
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// PLAYLIST ITEM PRIVACY STATUS //////
        def get_playlist_item_privacy_status(self, item_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="status",
                    id=item_id
                )
                response = request.execute()

                status = response["items"][0]["status"]["privacyStatus"]
                return status

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlist items with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_playlist_item_privacy_statuses(self, playlist_id: str) -> (list[dict] | None): 
            service = self.service

            try:
                request = service.playlistItems().list(
                    part="status",
                    playlistId=playlist_id
                )
                response = request.execute()
                statuses = []
                playlist_items = response["items"]
                for pitem in playlist_items:
                    statuses.append(pitem["status"]["privacyStatus"])
                return statuses
 
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no playlists with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
    #//////////// VIDEO ////////////
    class Video:

        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service

        #////// UTILITY METHODS //////                    
        def upload_video(self, video_path: str, title: str, description: str, privacy_status: str="public") -> (bool | None):
            """
            The upload_video(video_path, title, description, privacy_status), takes the 
            following parameters:

                video_path:     The local file path of the video you want to upload.
                title:          The title of the video.
                description:    The description of the video.
                privacy_status: (Optional) The privacy status of the uploaded video. It can 
                be set to "public," "private," or "unlisted." The default is "public."
                
            Before using this method or any method in this class, ensure you have the 
            get_authenticated_service() method defined as shown in the previous responses 
            to obtain an authenticated YouTube API service. This ensures that your 
            application is authorized to make API requests and has the necessary permissions 
            to upload videos on behalf of the user.

            """
            import requests
            from googleapiclient.errors import HttpError

            service = self.service

            try:
                request = service.videos().insert(
                    part="snippet,status",
                    body={
                        "snippet": {
                            "title": title,
                            "description": description
                        },
                        "status": {
                            "privacyStatus": privacy_status
                        }
                    }
                )
                response = request.execute()
                upload_url = response.get("uploadURL")
                if upload_url:
                    headers = {
                        "Authorization": f"Bearer {service.credentials.token}",
                        "Content-Type": "video/*"
                    }

                    video_file = open(video_path, "rb")
                    response = requests.put(upload_url, data=video_file, headers=headers)

                    if response.status_code == 200:
                        video_file.close()
                        return True
                    else:
                        video_file.close()
                        return False
                else:
                    return False
            except OSError as e:
                print(f"An OS error occurred: {e}")
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
        
        def video_exists(self, video_id: str) -> bool:
            try:
                if self.get_video(video_id) is not None:
                    return True
                return False                    
            except googleapiclient.errors.HttpError as e:
                return False
            except IndexError as e:
                return False
            except TypeError as te:
                return False
            except KeyError as ke:
                return False
                          
        def delete_video(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                service.videos().delete(
                    id=video_id
                ).execute()

                return True
            except OSError as e:
                print(f"An OS error occurred: {e}")
                None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def like_video(self, video_id: str) -> (bool | None):
            """
            This method like_video(video_id) takes the video_id of the video 
            you want to like and calls the videos.rate method with rating="like" 
            to like the video.
            """
            service = self.service

            try:
                request = service.videos().rate(
                    id=video_id,
                    rating="like"
                )
                response = request.execute()
                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def unlike_video(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                request = service.videos().rate(
                    id=video_id,
                    rating="none"
                )
                response = request.execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def save_video_to_playlist(self, playlist_id: str, video_id: str) -> (bool | None):
            """
            This method allows you to save a video specified by ID to a playlist
            also specified by ID.
            """
            service = self.service

            try:
                service.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def set_video_tags(self, video_id: str, tags: list[str]) -> (bool | None):
            """
            This method allows you to set the tags for a video with 
            the specified video_id. Provide a list of tags to update the video's tags.
            """
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                snippet = video["items"][0]["snippet"]
                snippet["tags"] = tags

                service.videos().update(
                    part="snippet",
                    body={
                        "id": video_id,
                        "snippet": snippet
                    }
                ).execute()

                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
    
        def update_video_privacy_status(self, video_id: str, privacy_status: str) -> (bool | None):
            """
            This function allows you to update the privacy status of a video 
            with the specified video_id. The privacy_status can be set to 
            "private," "public," or "unlisted."
            """
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                status = video["items"][0]["status"]
                status["privacyStatus"] = privacy_status

                service.videos().update(
                    part="status",
                    body={
                        "id": video_id,
                        "status": status
                    }
                ).execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def update_video_details(self, video_id: str, new_title: str=None, new_description: str=None, new_tags: list[str]=None) -> (bool | None):
            """
            This method allows you to update the title, description, and tags of a 
            video with the specified video_id. You can provide the new values for these 
            parameters, and the snippet will be updated accordingly.
            """
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                snippet = video["items"][0]["snippet"]
                if new_title:
                    snippet["title"] = new_title
                if new_description:
                    snippet["description"] = new_description
                if new_tags:
                    snippet["tags"] = new_tags

                service.videos().update(
                    part="snippet",
                    body={
                        "id": video_id,
                        "snippet": snippet
                    }
                ).execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
      
        def get_trending_videos(self, region_code: str="US", max_results: int=10) -> (list[dict] | None):
            service = self.service
            try:
                request = service.videos().list(
                    part="snippet",
                    chart="mostPopular",
                    regionCode=region_code,
                    maxResults=max_results
                )
                response = request.execute()

                trending = []
                for item in response["items"]:
                    trending.append(item)
                return trending

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError:\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// ENTIRE VIDEO RESOURCE //////
        def get_video(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                video_resource = video["items"][0]
                return video_resource

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        def get_videos_by_id(self, video_ids: list[str]) -> (list[dict] | None):
            service = self.service
            videos = []
            try:
                for id in video_ids:
                    video = service.videos().list(
                        part="snippet",
                        id=id
                    ).execute()

                    video_resource = video["items"][0]
                    videos.append(video_resource)
                return videos
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        def get_videos(self, max_results: int=10) -> (list[dict] | None):
            service = self.service
            try:
                request = service.videos().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                
                videos = []
                for video in response["items"]:
                    videos.append(video)
                return videos
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO KIND //////
        def get_video_kind(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                kind = video["items"][0]["kind"]
                return kind

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO ETAG //////
        def get_video_etag(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                etag = video["items"][0]["etag"]
                return etag

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO ID //////
        def get_video_id(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                id = video["items"][0]["id"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO SNIPPET PART //////
        def get_video_snippet(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                snippet = video["items"][0]["snippet"]
                return snippet

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO PUBLISHED DATETIME //////
        def get_video_publish_date(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                snippet = video["items"][0]["snippet"]["publishedAt"]
                return snippet

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO CHANNEL ID //////
        def get_video_channel_id(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                id = video["items"][0]["snippet"]["channelId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO TITLE //////
        def get_video_title(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                title = video["items"][0]["snippet"]["title"]
                return title
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO DESCRIPTION //////
        def get_video_description(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                description = video["items"][0]["snippet"]["description"]
                return description
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO THUMBNAILS //////
        def get_video_thumbnails(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnails = video["items"][0]["snippet"]["thumbnails"]
                return thumbnails
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
           
        def update_video_thumbnail_with_url(self, video_id: str, thumbnail_url: str) -> (bool | None):
            """
            This function allows you to update the thumbnail of a video using 
            a custom image URL. Provide the video_id of the video you want to update, 
            and the thumbnail_url that points to the new thumbnail image.
            """
            service = self.service
            try:
                request = service.videos().update(
                    part="snippet",
                    body={
                        "id": video_id,
                        "snippet": {
                            "thumbnails": {
                                "default": {
                                    "url": thumbnail_url
                                }
                            }
                        }
                    }
                )
                response = request.execute()

                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO DEFAULT RES THUMBNAIL //////
        def get_video_default_res_thumbnail(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["default"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_video_default_res_thumbnail_url(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                url = video["items"][0]["snippet"]["thumbnails"]["default"]["url"]
                return url
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_video_default_res_thumbnail_width(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                width = video["items"][0]["snippet"]["thumbnails"]["default"]["width"]
                return int(width)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_video_default_res_thumbnail_height(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                height = video["items"][0]["snippet"]["thumbnails"]["default"]["height"]
                return int(height)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO MEDIUM RES THUMBNAIL //////
        def get_video_medium_res_thumbnail(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["medium"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_video_medium_res_thumbnail_url(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                url = video["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
                return url
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_video_medium_res_thumbnail_width(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                width = video["items"][0]["snippet"]["thumbnails"]["medium"]["width"]
                return int(width)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_video_medium_res_thumbnail_height(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                height = video["items"][0]["snippet"]["thumbnails"]["medium"]["height"]
                return int(height)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// VIDEO HIGH RES THUMBNAIL //////
        def get_video_high_res_thumbnail(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["high"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_video_high_res_thumbnail_url(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                url = video["items"][0]["snippet"]["thumbnails"]["high"]["url"]
                return url
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_video_high_res_thumbnail_width(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                width = video["items"][0]["snippet"]["thumbnails"]["high"]["width"]
                return int(width)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_video_high_res_thumbnail_height(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                height = video["items"][0]["snippet"]["thumbnails"]["high"]["height"]
                return int(height)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// VIDEO STANDARD RES THUMBNAIL //////
        def get_video_standard_res_thumbnail(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["standard"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_video_standard_res_thumbnail_url(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["standard"]["url"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_video_standard_res_thumbnail_width(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                width = video["items"][0]["snippet"]["thumbnails"]["standard"]["width"]
                return int(width)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_video_standard_res_thumbnail_height(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                height = video["items"][0]["snippet"]["thumbnails"]["standard"]["height"]
                return int(height)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        #////// VIDEO MAX RES THUMBNAIL //////
        def get_video_max_res_thumbnail(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["maxres"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_video_max_res_thumbnail_url(self, video_id: str) -> (str | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                thumbnail = video["items"][0]["snippet"]["thumbnails"]["maxres"]["url"]
                return thumbnail
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        def get_video_max_res_thumbnail_width(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                width = video["items"][0]["snippet"]["thumbnails"]["maxres"]["width"]
                return int(width)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        def get_video_max_res_thumbnail_height(self, video_id: str) -> (int | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                height = video["items"][0]["snippet"]["thumbnails"]["maxres"]["height"]
                return int(height)
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        #////// VIDEO CHANNEL TITLE //////
        def get_video_channel_title(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                id = video["items"][0]["snippet"]["channelTitle"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// VIDEO TAGS //////
        def get_video_tags(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                tags = video["items"][0]["snippet"]["tags"]
                return tags

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def video_has_tag(self, video_id: str, tag: str) -> bool:
            service = self.service
            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()
                tags = video["items"][0]["snippet"]["tags"]

                for item in range(len(tags)):
                    if tags[item] == tag:
                        return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO CATEGORY ID //////
        def get_video_category_id(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                category_id = video["items"][0]["snippet"]["categoryId"]
                return category_id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE BROADCASTING CONTENT //////
        def get_video_live_broadcast_content(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                content = video["items"][0]["snippet"]["liveBroadcastContent"]
                return content

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// VIDEO DEFAULT LANGUAGE //////
        def get_video_default_language(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                lang = video["items"][0]["snippet"]["defaultLanguage"]
                return lang
                
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None   
        
        #////// VIDEO LOCALIZED DATA //////
        def get_video_localized_data(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                data = video["items"][0]["snippet"]["localized"]
                return data

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LOCALIZED TITLE //////
        def get_video_localized_title(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                title = video["items"][0]["snippet"]["localized"]["title"]
                return title

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LOCALIZED DESCRIPTION //////
        def get_video_localized_description(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                desc = video["items"][0]["snippet"]["localized"]["description"]
                return desc

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO DEFAULT AUDIO LANGUAGE //////
        def get_video_default_audio_language(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="snippet",
                    id=video_id
                ).execute()

                lang = video["items"][0]["snippet"]["defaultAudioLanguage"]
                return lang

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO CONTENT DETAILS PART //////
        def get_video_content_details(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                details = video["items"][0]["contentDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO DURATION //////
        def get_video_duration(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                duration = video["items"][0]["contentDetails"]["duration"]
                return duration

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO DIMENSION //////
        def get_video_dimension(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                dimension = video["items"][0]["contentDetails"]["dimension"]
                return dimension

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO DEFINITION //////
        def get_video_definition(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                definition = video["items"][0]["contentDetails"]["definition"]
                return definition

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO CAPTION //////
        def get_video_caption(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                caption = video["items"][0]["contentDetails"]["caption"]
                return caption

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LICENSED CONTENT //////
        def get_video_licensed_content(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                content = video["items"][0]["contentDetails"]["licensedContent"]
                return bool(content)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO REGION RESTRICTION //////
        def get_video_region_restriction(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                restriction = video["items"][0]["contentDetails"]["regionRestriction"]
                return restriction

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO REGION RESTRICTION ALLOWED //////
        def get_video_region_restriction_allowed(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                allowed = video["items"][0]["contentDetails"]["regionRestriction"]["allowed"]
                return allowed

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO REGION RESTRICTION BLOCKED //////
        def get_video_region_restriction_blocked(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                blocked = video["items"][0]["contentDetails"]["regionRestriction"]["blocked"]
                return blocked

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO CONTENT RATING //////
        def get_video_content_rating(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                rating = video["items"][0]["contentDetails"]["contentRating"]
                return rating

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROJECTION //////
        def get_video_projection(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                projection = video["items"][0]["contentDetails"]["projection"]
                return projection

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO HAS CUSTOM THUMBNAIL //////
        def video_has_custom_thumbnail(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="contentDetails",
                    id=video_id
                ).execute()

                custom = video["items"][0]["contentDetails"]["hasCustomThumbnail"]
                return bool(custom)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STATUS PART //////
        def get_video_status(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                status = video["items"][0]["status"]
                return status

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO UPLOAD STATUS //////
        def get_video_upload_status(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                status = video["items"][0]["status"]["uploadStatus"]
                return status

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO FAILURE REASON //////
        def get_video_failure_reason(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                reason = video["items"][0]["status"]["failureReason"]
                return reason

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO REJECTION REASON //////
        def get_video_rejection_reason(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                reason = video["items"][0]["status"]["rejectionReason"]
                return reason

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PRIVACY STATUS //////
        def get_video_privacy_status(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                status = video["items"][0]["status"]["privacyStatus"]
                return status

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PUBLISHED DATE //////
        def get_video_published_date(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                published = video["items"][0]["status"]["publishAt"]
                return published

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LICENSE //////
        def get_video_license(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                license = video["items"][0]["status"]["license"]
                return license

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO EMBEDDABLE //////
        def video_is_embeddable(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                embeddable = video["items"][0]["status"]["embeddable"]
                return bool(embeddable)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO PUBLIC STATS VIEWABLE //////
        def video_public_stats_viewable(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                viewable = video["items"][0]["status"]["publicStatsViewable"]
                return bool(viewable)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO MADE FOR KIDS //////
        def video_is_made_for_kids(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                for_kids = video["items"][0]["status"]["license"]
                return bool(for_kids)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO SELF DECLARED MADE FOR KIDS //////
        def video_self_declared_for_kids(self, video_id: str) -> (bool | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="status",
                    id=video_id
                ).execute()

                for_kids = video["items"][0]["status"]["license"]
                return bool(for_kids)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// VIDEO STATISTICS PART //////
        def get_video_statistics(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()

                rating = video["items"][0]["statistics"]
                return rating

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO VIEW COUNT //////
        def get_video_view_count(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()

                count = video["items"][0]["statistics"]["viewCount"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIKE COUNT //////
        def get_video_like_count(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()

                count = video["items"][0]["statistics"]["likeCount"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO DISLIKE COUNT //////
        def get_video_dislike_count(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()

                count = video["items"][0]["statistics"]["dislikeCount"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO FAVORITE COUNT //////
        def get_video_favorite_count(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()

                count = video["items"][0]["statistics"]["favoriteCount"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO COMMENT COUNT //////
        def get_video_comment_count(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="statistics",
                    id=video_id
                ).execute()

                count = video["items"][0]["statistics"]["commentCount"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PLAYER PART //////
        def get_video_player(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="player",
                    id=video_id
                ).execute()

                player = video["items"][0]["player"]
                return player

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PLAYER EMBED HTML //////
        def get_video_embed_html(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="player",
                    id=video_id
                ).execute()

                html = video["items"][0]["player"]["embedHtml"]
                return html

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PLAYER EMBED HEIGHT //////
        def get_video_embed_height(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="player",
                    id=video_id
                ).execute()

                height = video["items"][0]["player"]["embedHeight"]
                return float(height)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PLAYER EMBED WIDTH //////
        def get_video_embed_width(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="player",
                    id=video_id
                ).execute()

                width = video["items"][0]["player"]["embedWidth"]
                return float(width)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO TOPIC DETAILS PART //////
        def get_video_topic_details(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="topicDetails",
                    id=video_id
                ).execute()

                details = video["items"][0]["topicDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO TOPIC IDS //////
        def get_video_topic_ids(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="topicDetails",
                    id=video_id
                ).execute()

                ids = video["items"][0]["topicDetails"]["topicIds"]
                return ids

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO RELEVANT TOPIC IDS //////
        def get_video_relevant_topic_ids(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="topicDetails",
                    id=video_id
                ).execute()

                ids = video["items"][0]["topicDetails"]["relevantTopicIds"]
                return ids

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// VIDEO TOPIC CATEGORIES //////
        def get_video_topic_categories(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="topicDetails",
                    id=video_id
                ).execute()

                cats = video["items"][0]["topicDetails"]["topicCategories"]
                return cats

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO RECORDING DETAILS PART //////
        def get_video_recording_details(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="recordingDetails",
                    id=video_id
                ).execute()

                details = video["items"][0]["recordingDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO RECORDING DATE //////
        def get_video_recording_date(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="recordingDetails",
                    id=video_id
                ).execute()

                date = video["items"][0]["recordingDetails"]["recordingDate"]
                return date

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO FILE DETAILS PART //////
        def get_video_file_details(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                details = video["items"][0]["fileDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO FILE NAME //////
        def get_video_file_name(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                name = video["items"][0]["fileDetails"]["fileName"]
                return name

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO FILE SIZE //////
        def get_video_file_size(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                size = video["items"][0]["fileDetails"]["fileSize"]
                return size

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO FILE TYPE //////
        def get_video_file_type(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                type = video["items"][0]["fileDetails"]["fileType"]
                return type

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO CONTAINER //////
        def get_video_container(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                container = video["items"][0]["fileDetails"]["container"]
                return container

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS //////
        def get_video_streams(self, video_id: str) -> (list[dict] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                stream = video["items"][0]["fileDetails"]["videoStreams"]
                return stream

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS PIXEL WIDTH //////
        def get_video_streams_pixel_width(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                width = video["items"][0]["fileDetails"]["videoStreams"][0]["widthPixels"]
                return width

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS PIXEL HEIGHT //////
        def get_video_streams_pixel_height(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                height = video["items"][0]["fileDetails"]["videoStreams"][0]["heightPixels"]
                return height

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS FRAMERATE FPS //////
        def get_video_streams_framerate_fps(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                fps = video["items"][0]["fileDetails"]["videoStreams"][0]["frameRateFps"]
                return fps

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS ASPECT RATIO //////
        def get_video_streams_aspect_ratio(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                ratio = video["items"][0]["fileDetails"]["videoStreams"][0]["aspectRatio"]
                return ratio

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS CODEC //////
        def get_video_streams_codec(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                codec = video["items"][0]["fileDetails"]["videoStreams"][0]["codec"]
                return codec

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS BITRATE BPS //////
        def get_video_streams_bitrate_bps(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                bps = video["items"][0]["fileDetails"]["videoStreams"][0]["bitrateBps"]
                return float(bps)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS ROTATION //////
        def get_video_streams_rotation(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                rotation = video["items"][0]["fileDetails"]["videoStreams"][0]["rotation"]
                return rotation

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO STREAMS VENDOR //////
        def get_video_streams_vendor(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                vendor = video["items"][0]["fileDetails"]["videoStreams"][0]["vendor"]
                return vendor

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// AUDIO STREAMS //////
        def get_audio_streams(self, video_id: str) -> (list[dict] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                stream = video["items"][0]["fileDetails"]["audioStreams"]
                return stream

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// AUDIO STREAMS CHANNEL COUNT //////
        def get_audio_streams_channel_count(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                count = video["items"][0]["fileDetails"]["audioStreams"][0]["channelCount"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// AUDIO STREAMS CODEC //////
        def get_audio_streams_codec(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                codec = video["items"][0]["fileDetails"]["audioStreams"][0]["codec"]
                return codec

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// AUDIO STREAMS BITRATE BPS //////
        def get_audio_streams_bitrate_bps(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                bps = video["items"][0]["fileDetails"]["audioStreams"][0]["bitrateBps"]
                return float(bps)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// AUDIO STREAMS VENDOR //////
        def get_audio_streams_vendor(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                vendor = video["items"][0]["fileDetails"]["audioStreams"][0]["vendor"]
                return vendor

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO DURATION MS //////
        def get_video_duration_ms(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                count = video["items"][0]["fileDetails"]["durationMs"]
                return int(count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO BITRATE BPS //////
        def get_video_bitrate_bps(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                bps = video["items"][0]["fileDetails"]["bitrateBps"]
                return int(bps)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO CREATION TIME //////
        def get_video_creation_time(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="fileDetails",
                    id=video_id
                ).execute()

                time = video["items"][0]["fileDetails"]["creationTime"]
                return time

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING DETAILS PART //////
        def get_video_processing_deatils(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                details = video["items"][0]["processingDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING STATUS //////
        def get_video_processing_status(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                status = video["items"][0]["processingDetails"]["processingStatus"]
                return status

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING PROGRESS //////
        def get_video_processing_progress(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                progress = video["items"][0]["processingDetails"]["processingProgress"]
                return progress

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING PROGRESS PARTS TOTAL //////
        def get_video_processing_progress_parts_total(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                parts_total = video["items"][0]["processingDetails"]["processingProgress"]["partsTotal"]
                return parts_total

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING PROGRESS PARTS PROCESSED //////
        def get_video_processing_progress_parts_processed(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                parts_processed = video["items"][0]["processingDetails"]["processingProgress"]["partsProcessed"]
                return parts_processed

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING PROGRESS TIME LEFT MS //////
        def get_video_processing_progress_time_left_ms(self, video_id: str) -> (float | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                time = video["items"][0]["processingDetails"]["processingProgress"]["timeLeftMs"]
                return time

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING PROCESSING FAILURE REASON //////
        def get_video_processing_failure_reason(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                reason = video["items"][0]["processingDetails"]["processingFailureReason"]
                return reason

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING PROCESSING FILE DETAILS AVAILABILITY //////
        def get_video_processing_file_details_availability(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                availability = video["items"][0]["processingDetails"]["fileDetailsAvailability"]
                return availability

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING ISSUES AVAILABILITY //////
        def get_video_processing_issues_availability(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                availability = video["items"][0]["processingDetails"]["processingIssuesAvailability"]
                return availability

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING TAG SUGGESTIONS AVAILABILITY //////
        def get_video_processing_tag_suggestions_availability(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                availability = video["items"][0]["processingDetails"]["tagSuggestionsAvailability"]
                return availability

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING EDITOR SUGGESTIONS AVAILABILITY //////
        def get_video_processing_editor_suggestions_availability(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                availability = video["items"][0]["processingDetails"]["editorSuggestionsAvailability"]
                return availability

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO PROCESSING THUMBNAILS AVAILABILITY //////
        def get_video_processing_thumbnails_availability(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="processingDetails",
                    id=video_id
                ).execute()

                availability = video["items"][0]["processingDetails"]["thumbnailsAvailability"]
                return availability

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO SUGGESTIONS PART //////
        def get_video_suggestions(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="suggestions",
                    id=video_id
                ).execute()

                suggestions_part = video["items"][0]["suggestions"]
                return suggestions_part

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO SUGGESTIONS PROCESSING ERRORS //////
        def get_video_suggestions_processing_errors(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="suggestions",
                    id=video_id
                ).execute()

                errors = video["items"][0]["suggestions"]["processingErrors"]
                return errors

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO SUGGESTIONS PROCESSING WARNINGS //////
        def get_video_suggestions_processing_warnings(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="suggestions",
                    id=video_id
                ).execute()

                warns = video["items"][0]["suggestions"]["processingWarnings"]
                return warns

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO SUGGESTIONS PROCESSING HINTS //////
        def get_video_suggestions_processing_hints(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="suggestions",
                    id=video_id
                ).execute()

                hints = video["items"][0]["suggestions"]["processingHints"]
                return hints

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO TAG SUGGESTIONS //////
        def get_video_tag_suggestions(self, video_id: str) -> (list[dict] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="suggestions",
                    id=video_id
                ).execute()

                suggestions = video["items"][0]["suggestions"]["tagSuggestions"]
                return suggestions

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO EDITOR SUGGESTIONS //////
        def get_video_editor_suggestions(self, video_id: str) -> (list[str] | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="suggestions",
                    id=video_id
                ).execute()

                suggestions = video["items"][0]["suggestions"]["editorSuggestions"]
                return suggestions

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE STREAMING DETAILS PART //////
        def get_video_live_streaming_details(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                details = video["items"][0]["liveStreamingDetails"]
                return details

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE STREAMING ACTUAL START TIME //////
        def get_video_live_streaming_actual_start_time(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                time = video["items"][0]["liveStreamingDetails"]["actualStartTime"]
                return time 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE STREAMING ACTUAL END TIME //////
        def get_video_live_streaming_actual_end_time(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                time = video["items"][0]["liveStreamingDetails"]["actualEndTime"]
                return time 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE STREAMING SCHEDULED START TIME //////
        def get_video_live_streaming_scheduled_start_time(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                time = video["items"][0]["liveStreamingDetails"]["scheduledStartTime"]
                return time 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE STREAMING CONCURRENT VIEWERS //////
        def get_video_live_streaming_concurrent_viewers(self, video_id: str) -> (int | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                viewers = video["items"][0]["liveStreamingDetails"]["concurrentViewers"]
                return viewers

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LIVE STREAMING ACTIVE LIVE CHAT ID //////
        def get_video_live_streaming_active_live_chat_id(self, video_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                id = video["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
                return id 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// VIDEO LOCALIZATIONS PART //////
        def get_video_localizations(self, video_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()

                local = video["items"][0]["localizations"]
                return local 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
    #//////////// VIDEO CATEGORIES ////////////
    class VideoCategories:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service   
        
        def get_all_video_categories(self, country_code: str) -> (list[dict] | None):
            """
            This method retrieves all video categories available in a specific 
            region (identified by the regionCode). It prints information about 
            each category, including its ID and title.
            """
            service = self.service

            try:
                request = service.videoCategories().list(
                    part="snippet",
                    regionCode=f"{country_code}"
                )
                response = request.execute()
                categories = []
                for category in response["items"]:
                    category = {}
                    category["id"] = category["id"]
                    category["title"] = category["snippet"]["title"]
                    categories.append(category)
                return categories

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_video_category_by_id(self, category_id):
            """
            This method allows you to retrieve details about a specific 
            video category identified by its category_id. It prints information 
            about the category, including its title.
            """
            service = self.service

            try:
                request = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                )
                response = request.execute()

                if "items" in response:
                    category = response["items"][0]
                    category_title = category["snippet"]["title"]
                    print(f"Category ID: {category_id}, Title: {category_title}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_videos_in_category(self, category_id, max_results=10):
            """
            This method retrieves videos that belong to a specific video category, 
            identified by category_id. It prints information about each video, including 
            its title and video ID.
            """
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    type="video",
                    maxResults=max_results,
                    videoCategoryId=category_id
                )
                response = request.execute()

                for video in response["items"]:
                    video_title = video["snippet"]["title"]
                    video_id = video["id"]["videoId"]
                    print(f"Video Title: {video_title} (Video ID: {video_id})")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_most_popular_videos_in_category(self, category_id, max_results=10):
            """
            This method retrieves the most popular videos in a specific video category, 
            ordered by the number of views.
            """
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    type="video",
                    maxResults=max_results,
                    videoCategoryId=category_id,
                    order="viewCount"
                )
                response = request.execute()

                for video in response["items"]:
                    video_title = video["snippet"]["title"]
                    video_id = video["id"]["videoId"]
                    print(f"Video Title: {video_title} (Video ID: {video_id})")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def search_video_categories(self, query, max_results=10):
            """
            This method allows you to search for video categories using a query. 
            It prints information about each category that matches the search query.
            """
            service = self.service

            try:
                request = service.videoCategories().list(
                    part="snippet",
                    maxResults=max_results,
                    q=query
                )
                response = request.execute()

                for category in response["items"]:
                    category_id = category["id"]
                    category_title = category["snippet"]["title"]
                    print(f"Category ID: {category_id}, Title: {category_title}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_video_category_details(self, category_id):
            """
            This method retrieves details about a specific video category identified by 
            its category_id, including its title and whether it's assignable to videos.
            """
            service = self.service

            try:
                request = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                )
                response = request.execute()

                if "items" in response:
                    category = response["items"][0]
                    category_title = category["snippet"]["title"]
                    category_assignable = category["snippet"]["assignable"]
                    print(f"Category ID: {category_id}, Title: {category_title}, Assignable: {category_assignable}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
 
        #////// UTILITY METHODS //////
        def get_video_categories(self, region_code="US"):
            service = self.service

            try:
                request = service.videoCategories().list(
                    part="snippet",
                    regionCode=region_code
                )
                response = request.execute()

                for item in response["items"]:
                    print(f"{item['id']} - {item['snippet']['title']}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        #////// CATEGORY RESOURCE //////
        def get_video_categories_resource(self, category_id) -> (dict | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                resource = video["items"][0]
                return resource

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY KIND //////
        def get_video_category_kind(self, category_id) -> (str | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                kind = video["items"][0]["kind"]
                return kind 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY KIND //////
        def get_video_category_etag(self, category_id) -> (str | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                etag = video["items"][0]["etag"]
                return etag 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY ID //////
        def get_video_category_id(self, category_id) -> (str | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                id = video["items"][0]["id"]
                return id 

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY SNIPPET //////
        def get_video_category_snippet(self, category_id) -> (str | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                snip = video["items"][0]["snippet"]
                return snip

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY CHANNEL ID //////
        def get_video_category_channel_id(self, category_id) -> (str | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                id = video["items"][0]["snippet"]["channelId"]
                return id

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY CHANNEL TITLE //////
        def get_video_category_title(self, category_id) -> (str | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                title = video["items"][0]["snippet"]["title"]
                return title

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// CATEGORY ASSIGNABLE //////
        def video_category_is_assignable(self, category_id) -> (bool | None):
            service = self.service

            try:
                video = service.videoCategories().list(
                    part="snippet",
                    id=category_id
                ).execute()

                assignable = video["items"][0]["snippet"]["assignable"]
                return bool(assignable)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no video categories with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
    #//////////// VIDEO ABUSE REPORT REASON ////////////
    class VideoAbuseReportReason:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service

        #////// ENTIRE VIDEO ABUSE REPORT REASON RESOURCE //////
        def get_video_abuse_report_reason(self, reason: str) -> (dict | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["snippet"]["label"] == reason:
                        return item
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
        
        def get_all_video_abuse_report_reasons(self) -> (list[dict] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                reasons = []
                for item in resources:
                    reasons.append(item)
                return reasons

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
        
        #////// REPORT REASON KIND //////
        def get_video_abuse_report_reason_kind(self, reason_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["kind"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        def get_all_video_abuse_report_reason_kinds(self) -> (list[str] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                kinds = []
                for item in resources:
                    kinds.append(item["kind"])
                return kinds

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        #////// REPORT REASON ETAG //////
        def get_video_abuse_report_reason_etag(self, reason_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["etag"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        def get_all_video_abuse_report_reason_etags(self) -> (list[str] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                etags = []
                for item in resources:
                    etags.append(item["etag"])
                return etags

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        #////// REPORT REASON ID //////
        def get_video_abuse_report_reason_id(self, reason: str) -> (str | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["snippet"]["label"] == reason:
                        return item["id"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 

        def get_all_video_abuse_report_reason_ids(self) -> (list[str] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                ids = []
                for item in resources:
                    ids.append(item["id"])
                return ids

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
        
        #////// REPORT REASON SNIPPET //////
        def get_video_abuse_report_reason_snippet(self, reason_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["snippet"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        def get_all_video_abuse_report_reason_snippets(self) -> (list[dict] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                snippets = []
                for item in resources:
                    snippets.append(item["snippet"])
                return snippets

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        #////// REPORT REASON LABEL //////
        def get_video_abuse_report_reason_label(self, reason_id: str) -> (str | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["snippet"]["label"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
        
        def get_all_video_abuse_report_reason_labels(self) -> (list[str] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                labels = []
                for item in resources:
                    labels.append(item["snippet"]["label"])
                return labels

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        #////// REPORT REASON SECONDARY REASON //////
        def get_video_abuse_report_reason_secondary_reasons(self, reason_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["snippet"]["secondaryReasons"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        def get_all_video_abuse_report_reason_secondary_reasons(self) -> (list[dict] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                reasons = []
                for item in resources:
                    reasons.append(item["snippet"]["secondaryReasons"])
                return reasons

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        #////// REPORT REASON SECONDARY REASON ID //////
        def get_video_abuse_report_reason_secondary_reason_id(self, reason_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["snippet"]["secondaryReasons"]["id"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        def get_all_video_abuse_report_reason_secondary_reason_ids(self) -> (list[str] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                ids = []
                for item in resources:
                    ids.append(item["snippet"]["secondaryReasons"]["id"])
                return ids

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        #////// REPORT REASON SECONDARY REASON LABEL //////
        def get_video_abuse_report_reason_secondary_reason_label(self, reason_id: str) -> (dict | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                for item in resources:
                    if item["id"] == reason_id:
                        return item["snippet"]["secondaryReasons"]["label"]
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
        def get_all_video_abuse_report_reason_secondary_reason_labels(self) -> (list[str] | None):
            service = self.service

            try:
                video = service.videoAbuseReportReasons().list(
                    part="snippet",
                ).execute()

                resources = video["items"]
                labels = []
                for item in resources:
                    labels.append(item["snippet"]["secondaryReasons"]["label"])
                return labels

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"IndexError: Reason doesn't exist\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
          
    #//////////// CAPTION ////////////
    class Captions:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
            
        #////// UTILITY METHODS //////

        def download_caption_track(self, track_id: str, output_file: str) -> (bool | None):
            service = self.service
            try:
                request = service.captions().download(
                    id=track_id
                )
                with open(output_file, "wb") as file:
                    file.write(request.execute())
                    file.close()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def upload_caption_track(self, video_id: str, language: str, caption_file: str) -> (bool | None):
            service = self.service
            try:
                request = service.captions().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "language": language,
                            "name": "Caption Track",
                            "isDraft": False
                        }
                    },
                    media_body=googleapiclient.http.MediaFileUpload(caption_file, mimetype="text/vtt", resumable=True)
                )
                response = request.execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def delete_caption_track(self, track_id: str) -> (bool | None):
            service = self.service
            try:
                request = service.captions().delete(
                    id=track_id
                )
                response = request.execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def update_caption_track(self, track_id: str, language: str, new_name: str) -> (bool | None):
            """
            This function allows you to update the language and name of 
            an existing caption track identified by track_id.
            """
            service = self.service

            try:
                request = service.captions().update(
                    part="snippet",
                    body={
                        "id": track_id,
                        "snippet": {
                            "language": language,
                            "name": new_name
                        }
                    }
                )
                response = request.execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_upload_status(self, track_id: str) -> (str | None):
            """
            When you upload a new caption track, you can check the upload 
            status to see if it is still being processed. This can be helpful 
            if you want to wait until the caption track is fully available 
            before performing further operations.
            """
            service = self.service

            try:
                request = service.captions().list(
                    part="snippet",
                    id=track_id
                )
                response = request.execute()

                if "items" in response:
                    caption_track = response["items"][0]
                    status = caption_track["snippet"]["status"]["uploadStatus"]
                    if status == "succeeded":
                        return "succeeded"
                    elif status == "failed":
                        return "failed"
                    else:
                        return "processing"

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// ENTIRE CAPTION RESOURCE //////
        def get_all_captions(self, video_id: str) -> (list[dict] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                tracks = []
                for item in response["items"]:
                    tracks.append(item)
                return tracks
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption(self, caption_id: str, video_id: str=None) -> (dict | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// CAPTION TRACK KIND //////
        def get_all_caption_kinds(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                kinds = []
                for item in response["items"]:
                    kinds.append(item["kind"])
                return kinds
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_kind(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["kind"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// CAPTION TRACK ETAGS //////
        def get_all_caption_etags(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                etags = []
                for item in response["items"]:
                    etags.append(item["etag"])
                return etags
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_etag(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["etag"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// CAPTION TRACK IDS //////
        def get_all_caption_ids(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                ids = []
                for item in response["items"]:
                    ids.append(item["id"])
                return ids
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_id(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["id"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        #////// CAPTION TRACK SNIPPETS //////
        def get_all_caption_snippets(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                snippets = []
                for item in response["items"]:
                    snippets.append(item["snippet"])
                return snippets
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_snippet(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION TRACK VIDEO IDS //////
        def get_all_caption_video_ids(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                ids = []
                for item in response["items"]:
                    ids.append(item["snippet"]["videoId"])
                return ids
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_video_id(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["videoId"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION TRACK LAST UPDATED //////
        def get_all_captions_last_updates(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                dates = []
                for item in response["items"]:
                    dates.append(item["snippet"]["lastUpdated"])
                return dates
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_captions_last_update(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["lastUpdated"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION TRACK TRACK KIND //////
        def get_all_caption_track_kinds(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                kinds = []
                for item in response["items"]:
                    kinds.append(item["snippet"]["trackKind"])
                return kinds
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_track_kind(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["trackKind"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION TRACK LANGUAGE //////
        def get_all_caption_track_languages(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                langs = []
                for item in response["items"]:
                    langs.append(item["snippet"]["language"])
                return langs
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_track_language(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["language"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION TRACK NAME //////
        def get_caption_track_names(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                names = []
                for item in response["items"]:
                    names.append(item["snippet"]["name"])
                return names
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_track_name(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["name"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION AUDIO TRACK TYPE //////
        def get_caption_audio_track_types(self, video_id: str) -> (list[str] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                types = []
                for item in response["items"]:
                    types.append(item["snippet"]["audioTrackType"])
                return types
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_caption_audio_track_type(self, caption_id: str, video_id: str=None) -> (str | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["audioTrackType"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION IS CC //////
        def captions_are_cc(self, video_id: str) -> (list[dict] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answer = {}
                    answer[f"{item['id']}"] = bool(item['snippet']['isCC'])
                    answers.append(answer)
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_is_cc(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["isCC"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION IS LARGE //////
        def captions_are_large(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answer = {}
                    answer[f"{item['id']}"] = bool(item['snippet']['isLarge'])
                    answers.append(answer)
                    return answers
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_is_large(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["isLarge"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION IS EASY READER //////
        def captions_are_easy_readers(self, video_id: str) -> (list[dict] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answer = {}
                    answer[f"{item['id']}"] = bool(item['snippet']['isEasyReader'])
                    answers.append(answers)
                    return answers
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_is_easy_reader(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["isEasyReader"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION IS DRAFT //////
        def captions_are_drafts(self, video_id: str) -> (list[bool] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answer = {}
                    answer[f"{item['id']}"] = bool(item['snippet']['isDraft'])
                    answers.append(answer)
                    return answers
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_is_draft(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["isDraft"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION IS AUTO SYNCED //////
        def captions_are_auto_synced(self, video_id: str) -> (dict | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answer = {}
                    answer[f"{item['id']}"] = bool(item['snippet']['isAutoSynced'])
                    answers.append(answers)
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_is_auto_synced(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["isAutoSynced"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION STATUS //////
        def caption_statuses(self, video_id: str) -> (list[bool] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answers.append(bool(item["snippet"]["status"]))
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_status(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["status"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// CAPTION FAILURE REASON //////
        def caption_failure_reasons(self, video_id: str) -> (list[bool] | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id
                )
                response = request.execute()
                answers = []
                for item in response["items"]:
                    answers.append(bool(item["snippet"]["failureReason"]))
                return answers
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def caption_failure_reason(self, caption_id: str, video_id: str=None) -> (bool | None):
            service = self.service
            try:
                request = service.captions().list(
                    part="snippet",
                    id=caption_id,
                    videoId=video_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["failureReason"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
    #//////////// SUBSSCRIPTIONS ////////////
    class Subscriptions:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
    
        def subscribe_to_channel(self, channel_id: str) -> (bool | None):
            service = self.service

            try:
                request = service.subscriptions().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "resourceId": {
                                "kind": "youtube#channel",
                                "channelId": channel_id
                            }
                        }
                    }
                )
                response = request.execute()

                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def unsubscribe_from_channel(self, channel_id: str) -> (bool | None):
            service = self.service
            try:
                request = service.subscriptions().delete(
                    id=channel_id
                )
                response = request.execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        def iterate_subscriptions_in_channel(self, channel_id: str, func: object):
            """
            Iterate over the subscriptions in a channel.
            """
            service = self.service
            try:
                subscriptions = []

                request = service.subscriptions().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=50
                )
                while request is not None:
                    response = request.execute()

                    for item in response["items"]:
                        func(item)

                    request = service.subscriptions().list_next(request, response)

                return subscriptions

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_latest_subscriptions(self, max_results=10) -> (dict | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results,
                    order="newest"
                )
                response = request.execute()

                subscriptions = []
                for subscription in response["items"]:
                    channel_title = subscription["snippet"]["title"]
                    channel_id = subscription["snippet"]["resourceId"]["channelId"]
                    sub = {}
                    sub["title"] = channel_title
                    sub["id"] = channel_id
                    subscriptions.append(sub)
                return subscriptions
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_subscribed_channels(self, max_results: int=10) -> (dict | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                subscribed = {}
                for subscription in response["items"]:
                    channel_title = subscription["snippet"]["title"]
                    channel_id = subscription["snippet"]["resourceId"]["channelId"]
                    subscribed["title"] = channel_title
                    subscribed["id"] = channel_id
                return subscribed

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def is_subscribed_to_channel(self, channel_id: str) -> (bool | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True,
                    forChannelId=channel_id
                )
                response = request.execute()

                if "items" in response and len(response["items"]) > 0:
                    return True
                else:
                    return False

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_my_subscription_count(self) -> (int | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    mine=True
                )
                response = request.execute()

                subscription_count = response.get("pageInfo", {}).get("totalResults", 0)
                return int(subscription_count)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// ENTIRE SUBSCRIPTION RESOURCE //////
        def get_all_subscriptions(self) -> (list[dict] | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()

                subscriptions = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    subscriptions.append(sub)
                
                return subscriptions

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_subscription_by_index(self, channel_id: str=None, index: int=0) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                subscription_info = response["items"][index]
                return subscription_info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_subscription(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                subscription = response["items"][0]
                return subscription

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION KIND //////
        def get_subscription_kind(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                subscription = response["items"][0]["kind"]
                return subscription

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_kinds(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["kind"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION ETAG //////
        def get_subscription_etag(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["etag"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_etags(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["etag"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION ID //////
        def get_subscription_id(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["id"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_ids(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["id"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION SNIPPET //////
        def get_subscription_snippet(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_snippets(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION PUBLISH DATE //////
        def get_subscription_published_date(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["publishedAt"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_publish_dates(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["publishedAt"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION CHANNEL TITLE //////
        def get_subscription_channel_title(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["channelTitle"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_channel_titles(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["channelTitle"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION TITLE //////
        def get_subscription_title(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["title"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_titles(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["title"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION DESCRIPTION //////
        def get_subscription_description(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["description"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_descriptions(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["description"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION RESOURCE ID //////
        def get_subscription_resource_id(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["resourceId"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_resource_ids(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["resourceId"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION RESOURCE ID KIND //////
        def get_subscription_resource_id_kind(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["resourceId"]["kind"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_resource_id_kinds(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["resourceId"]["kind"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION RESOURCE ID CHANNEL ID //////
        def get_subscription_resource_id_channel_id(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["resourceId"]["channelId"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_resource_id_channel_ids(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["resourceId"]["channelIds"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION CHANNEL ID //////
        def get_subscription_channel_id(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["channelId"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_channel_ids(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["channelId"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// SUBSCRIPTION THUMBNAIL //////
        def get_subscription_thumbnail(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="snippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["snippet"]["thumbnail"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_thumbnails(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="snippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["snippet"]["thumbnail"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        #////// SUBSCRIPTION CONTENT DETAILS //////
        def get_subscription_content_details(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["contentDetails"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_content_details(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(sub["contentDetails"])
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        #////// SUBSCRIPTION TOTAL ITEM COUNT //////
        def get_subscription_total_item_count(self, sub_id: str, channel_id: str=None) -> (int | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["contentDetails"]["totalItemCount"]
                return int(info)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_total_item_counts(self) -> (list[int] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["contentDetails"]["totalItemCount"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// SUBSCRIPTION NEW ITEM COUNT //////
        def get_subscription_new_item_count(self, sub_id: str, channel_id: str=None) -> (int | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["contentDetails"]["newItemCount"]
                return int(info)

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_new_item_counts(self) -> (list[int] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["contentDetails"]["newItemCount"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// SUBSCRIPTION ACTIVITY TYPE //////
        def get_subscription_activity_type(self, sub_id: str, channel_id: str=None) -> (str | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["contentDetails"]["activityType"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscriptions_activity_types(self) -> (list[int] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="contentDetails",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["contentDetails"]["newItemCount"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// SUBSCRIPTION SUBSCRIBER SNIPPET //////
        def get_subscriber_snippet(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["subscriberSnippet"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscribers_snippets(self) -> (list[dict] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["subscriberSnippet"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// SUBSCRIPTION SUBSCRIBER TITLE //////
        def get_subscriber_title(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["subscriberSnippet"]["title"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscribers_titles(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["subscriberSnippet"]["title"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// SUBSCRIPTION SUBSCRIBER DESCRIPTION //////
        def get_subscriber_description(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["subscriberSnippet"]["description"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscribers_descriptions(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["subscriberSnippet"]["description"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
          
        #////// SUBSCRIPTION SUBSCRIBER CHANNEL ID //////
        def get_subscriber_channel_id(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["subscriberSnippet"]["channelId"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscribers_channel_ids(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["subscriberSnippet"]["channelId"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
         
        #////// SUBSCRIPTION SUBSCRIBER THUMBNAILS //////
        def get_subscriber_thumbnails(self, sub_id: str, channel_id: str=None) -> (dict | None):
            service = self.service

            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    id=sub_id,
                    channelId=channel_id,
                    mine=True
                )
                response = request.execute()

                info = response["items"][0]["subscriberSnippet"]["thumbnails"]
                return info

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no subscriptions with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_all_subscribers_thumbnails(self) -> (list[str] | None):
            service = self.service
            try:
                request = service.subscriptions().list(
                    part="subscriberSnippet",
                    mine=True
                )
                response = request.execute()
                info = []
                subscription_info = response["items"]
                for sub in subscription_info:
                    info.append(int(sub["subscriberSnippet"]["thumbnails"]))
                return info
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
             
    #//////////// MEMBERS ////////////
    class Members:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
    
    #//////////// MEMBERSHIPS LEVEL ////////////
    class MembershipsLevel:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        #////// ENTIRE MEMBERSHIPS LEVEL RESOURCE //////
        def get_memberships_level(self, channel_id: str, membership_level_id: str) -> (dict | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// MEMBERSHIPS LEVEL KIND //////
        def get_memberships_level_kind(self, channel_id: str, membership_level_id: str) -> (str | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["kind"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// MEMBERSHIPS LEVEL ETAG //////
        def get_memberships_level_etag(self, channel_id: str, membership_level_id: str) -> (str | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["etag"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// MEMBERSHIPS LEVEL ID //////
        def get_memberships_level_id(self, channel_id: str, membership_level_id: str) -> (str | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["id"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// MEMBERSHIPS LEVEL SNIPPET //////    
        def get_memberships_level_snippet(self, channel_id: str, membership_level_id: str) -> (dict | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["snippet"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// MEMBERSHIPS LEVEL CREATOR CHANNEL ID //////    
        def get_memberships_level_creator_channel_id(self, channel_id: str, membership_level_id: str) -> (str | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["snippet"]["creatorChannelId"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        #////// MEMBERSHIPS LEVEL DETAILS //////    
        def get_memberships_level_details(self, channel_id: str, membership_level_id: str) -> (str | None):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["snippet"]["levelDetails"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #////// MEMBERSHIPS LEVEL DISPLAY NAME //////    
        def get_memberships_level_display_name(self, channel_id: str, membership_level_id: str):
            try:
                request = self.service.members().list(
                    part="snippet",
                    channelId=channel_id,
                    id=membership_level_id
                )
                response = request.execute()
                
                if "items" in response:
                    return response["items"][0]["snippet"]["displayName"]
                else:
                    return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
    #//////////// COMMENT ////////////
    class Comment:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        #////// UTILITY METHODS //////
        def get_comment_replies(self, comment_id: str, max_results: int=10) -> (list[dict] | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    parentId=comment_id,
                    maxResults=max_results
                )
                response = request.execute()
                replies = []
                for item in response["items"]:
                    replies.append(item)
                return replies
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_comment_replies_text(self, comment_id: str, max_results: int=10) -> (list[str] | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    parentId=comment_id,
                    maxResults=max_results
                )
                response = request.execute()
                replies = []
                for item in response["items"]:
                    replies.append(item["snippet"]["textDisplay"])
                return replies
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def reply_to_comment(self, parent_comment_id: str, reply_text: str) -> (bool | None):
            service = self.service
            try:
                request = service.comments().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "parentId": parent_comment_id,
                            "textOriginal": reply_text
                        }
                    }
                )
                response = request.execute()
                return True
            except OSError as e:
                print(f"An OS error occurred: {e}")
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// ENTIRE COMMENT RESOURCE //////
        def get_comment(self, comment_id) -> (dict | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                
                return response["items"][0]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
    
        def edit_comment(self, comment_id: str, updated_text: str) -> (bool | None):
            service = self.service
            try:
                request = service.comments().update(
                    part="snippet",
                    body={
                        "id": comment_id,
                        "snippet": {
                            "textOriginal": updated_text
                        }
                    }
                )
                response = request.execute()
                return True
            except OSError as e:
                print(f"An OS error occurred: {e}")
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        def delete_comment(self, comment_id: str) -> (bool | None): 
            service = self.service
            try:
                service.comments().delete(
                    id=comment_id
                ).execute()

                return True
            except OSError as e:
                print(f"An OS error occurred: {e}")
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        #////// COMMENT KIND //////
        def get_comment_kind(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                
                return response["items"][0]["kind"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT ETAG //////
        def get_comment_etag(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                
                return response["items"][0]["etag"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT ID //////
        def get_comment_ids_for_video(self, video_id) -> (list[str] | None):
            try:
                request = self.service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=10  # Adjust as needed
                )
                response = request.execute()
                
                comment_ids = []
                for item in response.get("items", []):
                    comment_ids.append(item["snippet"]["topLevelComment"]["id"])
                
                return comment_ids
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return []
        
        #////// COMMENT SNIPPET //////
        def get_comment_snippet(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                
                return response["items"][0]["snippet"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT AUTHOR DISPLAY NAME //////
        def get_comment_author_display_name(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                
                return response["items"][0]["snippet"]["authorDisplayName"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT AUTHOR PROFILE IMAGE URL //////
        def get_comment_author_profile_image_url(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["authorProfileImageUrl"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// COMMENT AUTHOR CHANNEL URL //////
        def get_comment_author_channel_url(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["authorChannelUrl"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT AUTHOR CHANNEL ID //////
        def get_comment_author_channel_id(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["authorChannelId"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
            
        #////// COMMENT VALUE //////
        def get_comment_value(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["value"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT CHANNEL ID //////
        def get_comment_channel_id(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["channelId"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT VIDEO ID //////
        def get_comment_video_id(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["videoId"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT TEXT DISPLAY //////
        def get_comment_text_display(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["textDisplay"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT ORIGINAL TEXT //////
        def get_comment_original_text(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["textOriginal"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT PARENT ID //////
        def get_comment_parent_id(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["parentId"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT CAN RATE //////
        def comment_can_rate(self, comment_id) -> (bool | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return bool(response["items"][0]["snippet"]["canRate"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT VIEWER RATING //////
        def get_comment_viewer_rating(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["viewerRting"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT LIKE COUNT //////
        def get_comment_like_count(self, comment_id) -> (int | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return int(response["items"][0]["snippet"]["likeCount"])
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT MODERATION STATUS //////
        def get_comment_moderation_status(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["moderationStatus"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
           
        #////// COMMENT PUBLISH DATE //////
        def get_time_comment_published_at(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["publishedAt"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        #////// COMMENT UPDATED DATE //////
        def get_time_comment_updated_at(self, comment_id) -> (str | None):
            service = self.service
            try:
                request = service.comments().list(
                    part="snippet",
                    id=comment_id
                )
                response = request.execute()
                return response["items"][0]["snippet"]["updatedAt"]
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
               
    #//////////// COMMENT THREAD ////////////
    class CommentThread:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
    
        def get_video_comments(self, video_id: str, max_results: int=10) -> (list[dict] | None):
            service = self.service

            try:
                request = service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=max_results
                )
                response = request.execute()

                comments = []
                for item in response["items"]:
                    comments.append(item["snippet"]["topLevelComment"])

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
    
        def get_video_comments_text(self, video_id: str, max_results: int=10) -> (list[str] | None):
            service = self.service

            try:
                request = service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=max_results
                )
                response = request.execute()

                comments = []
                for item in response["items"]:
                    comments.append(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def post_video_comment(self, video_id: str, comment_text: str) -> (bool | None):
            service = self.service
            try:
                request = service.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": comment_text
                                }
                            }
                        }
                    }
                )
                response = request.execute()
                return True
            except OSError as e:
                print(f"An OS error occurred: {e}")
                return None
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None    

        def get_comment_thread_kind(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["kind"]            
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
                
        def get_comment_thread_etag(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["etag"]            
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
           
        def get_comment_thread_snippet(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]            
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
               
        def get_comment_thread_author_display_name(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["authorDisplayName"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_author_profile_image_url(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["authorProfileImageUrl"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_author_channel_id(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["authorChannelId"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_value(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["value"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_channel_id(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["channelId"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_video_id(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["videoId"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_text_display(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["textDisplay"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        def get_comment_thread_text_original(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["textOriginal"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
         
        def get_comment_thread_parent_id(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["parentId"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
             
        def comment_thread_can_rate(self, thread_id: str, video_id: str=None) -> (bool | None):
            service = self.service 
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()
                resource = response["items"][0]
                return bool(resource["snippet"]["canRate"])           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_viewer_rating(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["viewerRating"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_like_count(self, thread_id: str, video_id: str=None) -> (int | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return int(resource["snippet"]["likeCount"])           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_comment_thread_moderation_status(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["moderationStatus"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
         
        def get_time_comment_thread_published_at(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["publishedAt"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
          
        def get_time_comment_thread_updated_at(self, thread_id: str, video_id: str=None) -> (str | None):
            service = self.service
            
            try:
                request = service.commentThreads().list(
                    part="snippet",
                    id=thread_id,
                    videoId=video_id,
                )
                response = request.execute()

                resource = response["items"][0]
                return resource["snippet"]["updatedAt"]           
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no comments with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
    #//////////// THUMBNAIL ////////////
    class Thumbnail:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
    
        def upload_video_thumbnail(self, video_id: str, image_path: str) -> (bool | None):
            """
            This generator method allows you to upload a custom thumbnail image for a video. 
            Provide the video_id of the video you want to set the thumbnail for, and 
            the image_path which points to the local image file (in JPEG format) to 
            be uploaded.
            """
            service = self.service
            
            try:
                with open(image_path, "rb") as image_file:
                    thumbnail_data = image_file.read()

                request = service.thumbnails().set(
                    videoId=video_id,
                    media_body=googleapiclient.http.MediaIoBaseUpload(
                        io.BytesIO(thumbnail_data),
                        mimetype="image/jpeg",
                        chunksize=-1,
                        resumable=True
                    )
                )
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        yield int(status.progress() * 100)
                return True

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

    #//////////// WATERMARKS ////////////
    class WaterMark:
        """
        The WaterMark class requires authorization with at least one of 
        the following scopes:

          - https://www.googleapis.com/auth/youtubepartner
          - https://www.googleapis.com/auth/youtube.upload
          - https://www.googleapis.com/auth/youtube
          - https://www.googleapis.com/auth/youtube.force-ssl
        """
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
            
        #////// ENTIRE WATERMARK RESOURCE //////
        def get_watermark(self, channel_id: str) -> (dict | None):
            service = self.service

            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                watermark = response["watermark"]
                return watermark
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
         
        #////// WATERMARK TIMING PART //////
        def get_watermark_timing(self, channel_id: str) -> (dict | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                watermark_timing = response["watermark"]["timing"]
                return watermark_timing
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
             
        #////// WATERMARK TIMING TYPE //////
        def get_watermark_timing_type(self, channel_id: str) -> (str | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                _type = response["watermark"]["timing"]["type"]
                return _type
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        #////// WATERMARK TIMING OFFSET MS //////
        def get_watermark_timing_offset_ms(self, channel_id: str) -> (int | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                offset = response["watermark"]["timing"]["offsetMs"]
                return offset
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
         
        #////// WATERMARK TIMING DURATION MS //////
        def get_watermark_timing_duration_ms(self, channel_id: str) -> (int | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                duration = response["watermark"]["timing"]["durationMs"]
                return duration
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
        
        #////// WATERMARK POSITION PART //////
        def get_watermark_position(self, channel_id: str) -> (dict | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                position = response["watermark"]["position"]
                return position
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
             
        #////// WATERMARK POSITION TYPE //////
        def get_watermark_position_type(self, channel_id: str) -> (str | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                position_type = response["watermark"]["position"]["type"]
                return position_type
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
            
        #////// WATERMARK CORNER POSITION //////
        def get_watermark_corner_position(self, channel_id: str) -> (str | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                position = response["watermark"]["position"]["cornerPosition"]
                return position
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
         
        #////// WATERMARK IMAGE URL //////
        def get_watermark_image_url(self, channel_id: str) -> (str | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                url = response["watermark"]["imageUrl"]
                return url
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
         
        #////// WATERMARK IMAGE BYTES //////
        def get_watermark_image_bytes(self, channel_id: str) -> (str | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                bytez = response["watermark"]["imageBytes"]
                return bytez
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
         
        #////// WATERMARK TARGET CHANNEL ID //////
        def get_watermark_target_channel_id(self, channel_id: str) -> (str | None):
            service = self.service
            try:
                request = service.watermarks().set(
                    channelId=channel_id
                )
                response = request.execute()
                id = response["watermark"]["targetChannelId"]
                return id
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None 
         
    #//////////// ACTIVITY ////////////
    class Activity:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
            
        def get_my_recent_activities(self, max_results=10):
            """
            This function retrieves recent activities for the authenticated user. 
            It prints information about uploaded videos, liked videos, and comments 
            made by the user.
            """
            service = self.service
            try:
                request = service.activities().list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=max_results
                )
                response = request.execute()
                for activity in response["items"]:
                    activity_type = activity["snippet"]["type"]
                    if activity_type == "upload":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["upload"]["videoId"]
                        print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "like":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                        print(f"Liked Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "comment":
                        comment_text = activity["snippet"]["displayMessage"]
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["comment"]["videoId"]
                        print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_activities_by_type(self, activity_type, max_results=10):
            """
            This method will retrieve activities of a specific type for the authenticated user. 
            (e.g., "upload", "like", or "comment") 
            """
            service = self.service

            try:
                request = service.activities().list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=max_results,
                    type=activity_type
                )
                response = request.execute()

                for activity in response["items"]:
                    if activity_type == "upload":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["upload"]["videoId"]
                        print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "like":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                        print(f"Liked Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "comment":
                        comment_text = activity["snippet"]["displayMessage"]
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["comment"]["videoId"]
                        print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_activities_since_date(self, start_date, max_results=10):
            """
            This method retrieves activities for the authenticated user since a 
            specific date (provided as start_date).
            """
            service = self.service

            try:
                request = service.activities().list(
                    part="snippet,contentDetails",
                    mine=True,
                    maxResults=max_results,
                    publishedAfter=start_date
                )
                response = request.execute()

                for activity in response["items"]:
                    activity_type = activity["snippet"]["type"]
                    if activity_type == "upload":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["upload"]["videoId"]
                        print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "like":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                        print(f"Liked Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "comment":
                        comment_text = activity["snippet"]["displayMessage"]
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["comment"]["videoId"]
                        print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_video_activities_by_channel(self, channel_id, max_results=10):
            """
            This method retrieves video upload activities for a specific 
            channel (identified by channel_id).
            """
            service = self.service

            try:
                request = service.activities().list(
                    part="snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=max_results,
                    type="upload"
                )
                response = request.execute()

                for activity in response["items"]:
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["upload"]["videoId"]
                    print(f"Uploaded Video: {video_title} (Video ID: {video_id})")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_channel_activity(self, channel_id, max_results=10):
            service = self.service

            try:
                request = service.activities().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=max_results
                )
                response = request.execute()

                for activity in response["items"]:
                    print(activity["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_channel_activities(self, channel_id, max_results=10):
            """
            This method retrieves recent activities on a specific channel. 
            It prints information about uploaded videos, liked videos, and 
            comments made on the channel.
            """
            service = self.service

            try:
                request = service.activities().list(
                    part="snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=max_results
                )
                response = request.execute()

                for activity in response["items"]:
                    activity_type = activity["snippet"]["type"]
                    if activity_type == "upload":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["upload"]["videoId"]
                        print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "like":
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                        print(f"Liked Video: {video_title} (Video ID: {video_id})")
                    elif activity_type == "comment":
                        comment_text = activity["snippet"]["displayMessage"]
                        video_title = activity["snippet"]["title"]
                        video_id = activity["contentDetails"]["comment"]["videoId"]
                        print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_subscription_activity(self, max_results=10):
            service = self.service

            try:
                request = service.activities().list(
                    part="snippet,contentDetails",
                    home=True,
                    maxResults=max_results
                )
                response = request.execute()

                for activity in response["items"]:
                    channel_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["upload"]["videoId"]
                    print(f"New Upload from {channel_title}: https://www.youtube.com/watch?v={video_id}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_activities_from_playlist(self, playlist_id, max_results=10):
            """
            This method retrieves activities (videos) from a specific playlist. 
            It prints information about videos contained within the playlist.
            """
            service = self.service
            try:
                request = service.playlistItems().list(
                    part="snippet",
                    playlistId=playlist_id,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    video_title = item["snippet"]["title"]
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    print(f"Video in Playlist: {video_title} (Video ID: {video_id})")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
    
    #//////////// SEARCH ////////////
    class Search:  
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
            
        def search_channels(self, query, max_results=10):
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="channel",
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")        
            
        def get_channel_id_by_name(self, channel_name: str) -> (str | None):
            """ 
            This method takes the channel_name as input and returns 
            the corresponding channel ID. It uses the search.list method 
            with the type="channel" parameter to filter the results and
            fetches the first channel ID that matches the search query.
            """
            service = self.service

            try:
                request = service.search().list(
                    part="id",
                    q=channel_name,
                    type="channel",
                    maxResults=1
                )
                response = request.execute()

                if "items" in response:
                    channel_id = response["items"][0]["id"]["channelId"]
                    return channel_id
                else:
                    print("Channel not found.")
                    return None

            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no channels with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def search_videos(self, query, max_results=10):
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")        

        def search_videos_by_order(self, query, order="relevance", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    order=order,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def search_videos_by_category(self, query, category_id, max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    videoCategoryId=category_id,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def search_videos_by_definition(self, query, definition="any", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    videoDefinition=definition,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def search_videos_by_duration(self, query, duration="any", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    videoDuration=duration,
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")    

        def search_videos_by_license(self, query, license_type="any", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    videoLicense=license_type,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def search_videos_by_type(self, query, video_type="any", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type=video_type,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def search_embeddable_videos(self, query, embeddable="true", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    videoEmbeddable=embeddable,
                    maxResults=max_results
                )
                response = request.execute()
                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def search_videos_by_published_date(self, query, published_after, published_before, max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    publishedAfter=published_after,
                    publishedBefore=published_before,
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_channel_videos(self, channel_id: str, max_results: int=100) -> (list[dict] | None):
            service = self.service
            try:
                request = service.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                maxResults=max_results
                )
                response = request.execute()
                videos = []
                for item in response["items"]:
                    videos.append(item)
                return videos
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no channels with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        def iterate_related_videos(self, video_id, max_results=10):
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    relatedToVideoId=video_id,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()

                related_videos = response.get("items", [])
                for video in related_videos:
                    video_id = video["id"]["videoId"]
                    video_title = video["snippet"]["title"]
                    channel_title = video["snippet"]["channelTitle"]
                    print(f"Video ID: {video_id}, Title: {video_title}, Channel: {channel_title}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_related_videos(self, video_id, max_results=10):
            """
            This method retrieves related videos for a specific video. It prints 
            information about videos related to the given video based on YouTube's 
            recommendation algorithm.
            """
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    relatedToVideoId=video_id,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()

                for video in response["items"]:
                    title = video["snippet"]["title"]
                    video_id = video["id"]["videoId"]
                    print(f"Related Video: {title} (Video ID: {video_id})")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_videos_by_category(self, category_id, region_code="US", max_results=10):
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    videoCategoryId=category_id,
                    regionCode=region_code,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_videos_by_tag(self, tag, region_code="US", max_results=10):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=tag,
                    regionCode=region_code,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_recommended_videos(self, video_id, max_results=10):
            """
            This method will get recommended videos based on a given video's ID.
            """
            service = self.service

            try:
                # Get recommended videos for the given video ID
                request = service.search().list(
                    part="snippet",
                    relatedToVideoId=video_id,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()

                recommended_videos = []
                for item in response["items"]:
                    video = item["snippet"]
                    recommended_videos.append({
                        "video_id": item["id"]["videoId"],
                        "title": video["title"],
                        "channel": video["channelTitle"]
                    })

                return recommended_videos

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
                return None
        
        def get_popular_video_thumbnails(self, channel_id: str, max_results: int=10) -> (list[dict] | None):
            """
            This function retrieves the most popular video thumbnails for 
            a specific channel, ordered by the number of views. It provides 
            the video titles, IDs, and medium-sized thumbnail URLs.
            """
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=max_results,
                    order="viewCount",
                    type="video"
                )
                response = request.execute()
                urls = []
                for video in response["items"]:
                    urls.append(video["snippet"]["thumbnails"]["medium"]["url"])
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no videos with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
        
        def get_videos_by_categories(self, category_ids, max_results=10):
            """
            This method allows you to retrieve videos that belong to multiple video categories. 
            Provide a list of category_ids, and it will return videos that are associated with 
            any of the specified categories.
            """
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    type="video",
                    maxResults=max_results,
                    videoCategoryId=",".join(category_ids)
                )
                response = request.execute()

                for video in response["items"]:
                    video_title = video["snippet"]["title"]
                    video_id = video["id"]["videoId"]
                    print(f"Video Title: {video_title} (Video ID: {video_id})")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
 
    #//////////// LIVE BROADCASTS ///////////
    class LiveBroadcast:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        def get_live_streams(self, max_results=10):
            service = self.service
            try:
                request = service.liveStreams().list(
                    part="snippet",
                    maxResults=max_results
                )
                response = request.execute()

                for stream in response["items"]:
                    print(stream["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_live_broadcasts(self, max_results=10):
            service = self.service
            try:
                request = service.liveBroadcasts().list(
                    part="snippet",
                    maxResults=max_results
                )
                response = request.execute()

                for broadcast in response["items"]:
                    print(broadcast["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def search_live_broadcasts(self, query, max_results=10):
            service = self.service

            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    eventType="live",
                    maxResults=max_results
                )
                response = request.execute()

                for item in response["items"]:
                    print(item["snippet"]["title"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_live_chat_messages(self, live_chat_id, max_results=10):
            service = self.service
            try:
                request = service.liveChatMessages().list(
                    liveChatId=live_chat_id,
                    part="snippet",
                    maxResults=max_results
                )
                response = request.execute()

                for message in response["items"]:
                    print(message["snippet"]["displayMessage"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_live_chat_moderators(self, live_chat_id, max_results=10):
            service = self.service
            try:
                request = service.liveChatModerators().list(
                    liveChatId=live_chat_id,
                    part="snippet",
                    maxResults=max_results
                )
                response = request.execute()

                for moderator in response["items"]:
                    print(moderator["snippet"]["moderatorDetails"]["displayName"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_live_chat_bans(self, live_chat_id, max_results=10):
            service = self.service

            try:
                request = service.liveChatBans().list(
                    liveChatId=live_chat_id,
                    part="snippet",
                    maxResults=max_results
                )
                response = request.execute()

                for ban in response["items"]:
                    print(ban["snippet"]["bannedUserDetails"]["displayName"])

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def insert_live_chat_message(self, live_chat_id, message_text):
            service = self.service
            try:
                request = service.liveChatMessages().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "liveChatId": live_chat_id,
                            "type": "textMessageEvent",
                            "textMessageDetails": {
                                "messageText": message_text
                            }
                        }
                    }
                )
                response = request.execute()

                print("Live chat message sent successfully!")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_all_live_chat_details(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _details = (
                    chat['liveChatId'], 
                    chat['liveChatType'], 
                    chat['title'], 
                    chat['description'],
                    chat['isModerated'], 
                    chat['scheduledStartTime'], 
                    status['actualStartTime'],
                    status['lifeCycleStatus'], 
                    status['activeLiveChatId'], 
                    status['concurrentViewers'],
                    status['activeParticipants']
                )
                return _details
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
                
        def get_live_chat_id(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _id = chat['liveChatId']
                return _id
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_live_chat_type(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _type = chat['liveChatType']
                return _type
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_live_chat_title(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _title = chat['title']
                return _title
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_live_chat_description(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _description = chat['description']
                return _description
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def is_live_chat_moderated(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _is_moderated = chat['isModerated']
                return _is_moderated
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_live_chat_scheduled_start_time(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _description = chat['scheduledStartTime']
                return _description
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_live_chat_actual_start_time(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _actual_start_time = status['actualStartTime']
                return _actual_start_time
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_live_chat_life_cycle_status(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _life_cycle_status = status['lifeCycleStatus']
                return _life_cycle_status
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_active_live_chat_id(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _active_chat_id = status['activeLiveChatId']
                return _active_chat_id
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
        
        def get_live_chat_concurrent_viewers(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _concurrent_viewers = status['concurrentViewers']
                return _concurrent_viewers
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_live_chat_active_participants(self, live_chat_id):
            service = self.service
            try:
                request = service.liveChat().list(
                    id=live_chat_id,
                    part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
                )
                response = request.execute()
                chat = response["items"][0]["snippet"]
                status = response["items"][0]["status"]
                _active_participants = status['activeParticipants']
                return _active_participants
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")
    
    #//////////// LOCALIZATION /////////////
    class Localization:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
            
        def verify_video(self, video_id: str, country_code: str) -> (bool | None):
            """
            Verify if a video is available in a specific country using its ID.
            """
            service = self.service
            try:
                request = service.videos().list(
                    part="status",
                    id=video_id,
                    regionCode=country_code
                )
                response = request.execute()
                video_status = response["items"][0]["status"]
                is_available = video_status["uploadStatus"] == "processed" and video_status["privacyStatus"] == "public"
                return is_available
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def search_videos_by_location(self, query: str, location: str, location_radius: float, max_results: int=10) -> (list[dict] | None):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    location=location,
                    locationRadius=location_radius,
                    maxResults=max_results
                )
                response = request.execute()
                videos = []
                for item in response["items"]:
                    videos.append(item["snippet"]["title"])
                return videos
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError: No data.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def search_videos_by_language(self, query: str, language_code: str, max_results: int=10) -> (list[dict] | None):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    relevanceLanguage=language_code,
                    maxResults=max_results
                )
                response = request.execute()
                videos = []
                for item in response["items"]:
                    videos.append(item["snippet"]["title"])
                return videos
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"IndexError: No data .\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None

        def get_video_details_in_languages(self, video_id: str, languages: str ) -> (dict | None):
            """
            This method allows you to retrieve video details (title and description) in 
            different languages for a specific video identified by its video_id.
            """
            service = self.service

            try:
                for language in languages:
                    request = service.videos().list(
                        part="snippet",
                        id=video_id,
                        hl=language
                    )
                    response = request.execute()
                    details = []
                    if "items" in response:
                        video = response["items"][0]
                        detail = {}
                        detail["title"] = video["snippet"]["title"]
                        detail["description"] = video["snippet"]["description"]
                        details.append(detail)
                    return details

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_videos_by_language(self, language_code: str, region_code: str="US", max_results: int=10) -> (list[str] | None):
            service = self.service
            try:
                request = service.search().list(
                    part="snippet",
                    regionCode=region_code,
                    relevanceLanguage=language_code,
                    type="video",
                    maxResults=max_results
                )
                response = request.execute()
                titles = []
                for item in response["items"]:
                    titles.append(item["snippet"]["title"])
                return titles
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as e:
                print(f"There are no videos with the given ID.\n{e}")
                return None
            except TypeError as e:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{e}")
                return None
            except KeyError as e:
                print(f"Key error: Bad key. Field doesn't exists!\n{e}")
                return None
        
        def get_video_category_by_region_and_language(self, region_code , language_code):
            """
            This method retrieves video categories available in a specific region_code and 
            language_code. It prints information about each category, including its ID and title.
            """
            service = self.service

            try:
                request = service.videoCategories().list(
                    part="snippet",
                    regionCode=region_code,
                    hl=language_code
                )
                response = request.execute()

                for category in response["items"]:
                    category_id = category["id"]
                    category_title = category["snippet"]["title"]
                    print(f"Category ID: {category_id}, Title: {category_title}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def set_video_localizations(self, video_id, localizations):
            """
            This method allows you to set the title and description of a video 
            in different languages. Provide a dictionary localizations where the 
            keys are language codes, and the values are dictionaries containing 
            the localized title and description for each language.
            """
            service = self.service

            try:
                for language, localization_data in localizations.items():
                    title = localization_data.get("title", "")
                    description = localization_data.get("description", "")

                    request = service.videos().update(
                        part="snippet",
                        body={
                            "id": video_id,
                            "snippet": {
                                "title": title,
                                "description": description,
                                "defaultLanguage": language
                            }
                        }
                    )
                    response = request.execute()

                    print(f"Video details for language {language} updated successfully!")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_channel_details_in_languages(self, channel_id, languages):
            """
            This method allows you to retrieve channel details (title and description) in 
            different languages for a specific channel identified by its channel_id.
            """
            service = self.service

            try:
                for language in languages:
                    request = service.channels().list(
                        part="snippet",
                        id=channel_id,
                        hl=language
                    )
                    response = request.execute()

                    if "items" in response:
                        channel = response["items"][0]
                        channel_title = channel["snippet"]["title"]
                        channel_description = channel["snippet"]["description"]
                        print(f"Language: {language}, Channel Title: {channel_title}, Description: {channel_description}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def set_channel_localizations(self, channel_id, localizations):
            """
            This method allows you to set the title and description of a channel in 
            different languages. Provide a dictionary localizations where the keys are 
            language codes, and the values are dictionaries containing the localized 
            title and description for each language
            """
            service = self.service

            try:
                for language, localization_data in localizations.items():
                    title = localization_data.get("title", "")
                    description = localization_data.get("description", "")

                    request = service.channels().update(
                        part="snippet",
                        body={
                            "id": channel_id,
                            "snippet": {
                                "title": title,
                                "description": description,
                                "defaultLanguage": language
                            }
                        }
                    )
                    response = request.execute()

                    print(f"Channel details for language {language} updated successfully!")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def list_available_caption_languages(self, video_id):
            """
            This method will retrieve a list of the available languages 
            for caption tracks on YouTube.
            """
            service = self.service

            try:
                request = service.captions().list(
                    part="snippet",
                    videoId=f"{video_id}"
                )
                response = request.execute()

                languages = set()
                for caption_track in response["items"]:
                    language = caption_track["snippet"]["language"]
                    languages.add(language)

                print("Available caption languages:")
                for language in languages:
                    print(language)

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_captions_in_languages(self, video_id, languages):
            """
            This method allows you to retrieve captions (subtitles) for a \
            video in different languages. Provide a list of language codes, and 
            it will return information about each caption in the specified languages.
            """
            service = self.service

            try:
                for language in languages:
                    request = service.captions().list(
                        part="snippet",
                        videoId=video_id,
                        hl=language
                    )
                    response = request.execute()

                    if "items" in response:
                        caption = response["items"][0]
                        caption_language = caption["snippet"]["language"]
                        caption_name = caption["snippet"]["name"]
                        print(f"Language: {caption_language}, Caption Name: {caption_name}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def set_captions_localizations(self, caption_track_id, localizations):
            """
            This method allows you to set the name and language of a caption track 
            in different languages. Provide a dictionary localizations where the keys 
            are language codes, and the values are dictionaries containing the localized 
            caption name and language for each language.
            """
            service = self.service

            try:
                for language, localization_data in localizations.items():
                    caption_name = localization_data.get("caption_name", "")
                    caption_language = localization_data.get("caption_language", "")

                    request = service.captions().update(
                        part="snippet",
                        body={
                            "id": caption_track_id,
                            "snippet": {
                                "name": caption_name,
                                "language": caption_language
                            }
                        }
                    )
                    response = request.execute()

                    print(f"Caption details for language {caption_language} updated successfully!")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def get_thumbnails_in_languages(self, video_id, languages):
            """
            This method allows you to retrieve video thumbnails in different languages. 
            Provide a list of language codes, and it will return the URL of the default 
            thumbnail in each specified language
            """
            service = self.service

            try:
                for language in languages:
                    request = service.thumbnails().set(
                        videoId=video_id,
                        language=language
                    )
                    response = request.execute()

                    if "items" in response:
                        thumbnails = response["items"]
                        thumbnail_default = thumbnails[0]["default"]["url"]
                        print(f"Language: {language}, Default Thumbnail URL: {thumbnail_default}")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

        def set_thumbnail_localizations(self, video_id, localizations):
            """
            This method allows you to set the thumbnail URL for a video in 
            different languages. Provide a dictionary localizations where the 
            keys are language codes, and the values are dictionaries containing 
            the localized thumbnail URL for each language.
            """
            service = self.service

            try:
                for language, localization_data in localizations.items():
                    thumbnail_url = localization_data.get("thumbnail_url", "")

                    request = service.thumbnails().set(
                        videoId=video_id,
                        language=language,
                        media_body=thumbnail_url
                    )
                    response = request.execute()

                    print(f"Thumbnail URL for language {language} set successfully!")

            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred: {e}")

    #//////////// ABUSE REPORT ///////////
    class AbuseReport:
        def __init__(self, ytd_api_tools: object) -> None:
            self.service = ytd_api_tools.service
        
        def report_video(self, video_id: str, reason: str, additional_comments=None) -> (bool | None):
            """
            This method allows users to report a video for abuse. The reason parameter 
            specifies the reason for reporting, and additional_comments can be used to 
            provide additional context.
            """
            service = self.service

            try:
                request = service.videos().reportAbuse(
                    part="snippet",
                    videoId=video_id,
                    reasonId=reason,
                    comments=additional_comments
                )
                response = request.execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def report_channel(self, channel_id: str, reason: str, additional_comments=None) -> (bool | None):
            """
            This method allows users to report a channel for abuse. The reason parameter 
            specifies the reason for reporting, and additional_comments can be used to 
            provide additional context.
            """
            service = self.service
            try:
                request = service.channels().reportAbuse(
                    part="snippet",
                    channelId=channel_id,
                    reasonId=reason,
                    comments=additional_comments
                )
                response = request.execute()

                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def report_playlist(self, playlist_id: str, reason: str, additional_comments=None) -> (bool | None):
            """
            This method allows users to report a playlist for abuse. The reason 
            parameter specifies the reason for reporting, and additional_comments 
            can be used to provide additional context
            """
            service = self.service
            try:
                request = service.playlists().reportAbuse(
                    part="snippet",
                    playlistId=playlist_id,
                    reasonId=reason,
                    comments=additional_comments
                )
                response = request.execute()
                return True
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        def get_abuse_report_reason_categories(self) -> (list[dict] | None):
            """
            This method retrieves the categories of abuse report reasons 
            available on YouTube. It lists the categories and their corresponding IDs.
            """
            service = self.service
            try:
                request = service.videoAbuseReportReasons().list(
                    part="snippet"
                )
                response = request.execute()
                cats = []
                for reason_category in response["items"]:
                    cats.append(reason_category)
                return cats
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None
 
        def get_abuse_report_reasons_in_category(self, category_id: str) -> (list[dict] | None):
            """
            This method retrieves the abuse report reasons available within 
            a specific category_id. It lists the reasons and their corresponding IDs.
            """
            service = self.service
            try:
                request = service.videoAbuseReportReasons().list(
                    part="snippet",
                    hl="en",
                    videoId=category_id
                )
                response = request.execute()
                reasons = []
                for reason in response["items"]:
                    reasons.append(reason)
                return reasons
            except googleapiclient.errors.HttpError as e:
                print(f"An API error occurred: {e}")
                return None
            except IndexError as ie:
                print(f"There are no comments with the given ID.\n{ie}")
                return None
            except TypeError as te:
                print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                return None
            except KeyError as ke:
                print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                return None

        #//////////// VIDEO ABUSE REPORT REASON ////////////
        class VideoAbuseReportReason:
            def __init__(self, ytd_api_tools: object) -> None:
                self.service = ytd_api_tools.service

            #////// ENTIRE VIDEO ABUSE REPORT REASON RESOURCE //////
            def get_video_abuse_report_reason(self, reason: str) -> (dict | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["snippet"]["label"] == reason:
                            return item
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            def get_all_video_abuse_report_reasons(self) -> (list[dict] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    reasons = []
                    for item in resources:
                        reasons.append(item)
                    return reasons

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            #////// REPORT REASON KIND //////
            def get_video_abuse_report_reason_kind(self, reason_id: str) -> (str | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["kind"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
                
            def get_all_video_abuse_report_reason_kinds(self) -> (list[str] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    kinds = []
                    for item in resources:
                        kinds.append(item["kind"])
                    return kinds

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
                
            #////// REPORT REASON ETAG //////
            def get_video_abuse_report_reason_etag(self, reason_id: str) -> (str | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["etag"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
                
            def get_all_video_abuse_report_reason_etags(self) -> (list[str] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    etags = []
                    for item in resources:
                        etags.append(item["etag"])
                    return etags

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
                
            #////// REPORT REASON ID //////
            def get_video_abuse_report_reason_id(self, reason: str) -> (str | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["snippet"]["label"] == reason:
                            return item["id"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 

            def get_all_video_abuse_report_reason_ids(self) -> (list[str] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    ids = []
                    for item in resources:
                        ids.append(item["id"])
                    return ids

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            #////// REPORT REASON SNIPPET //////
            def get_video_abuse_report_reason_snippet(self, reason_id: str) -> (dict | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["snippet"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            def get_all_video_abuse_report_reason_snippets(self) -> (list[dict] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    snippets = []
                    for item in resources:
                        snippets.append(item["snippet"])
                    return snippets

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
                
            #////// REPORT REASON LABEL //////
            def get_video_abuse_report_reason_label(self, reason_id: str) -> (str | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["snippet"]["label"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            def get_all_video_abuse_report_reason_labels(self) -> (list[str] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    labels = []
                    for item in resources:
                        labels.append(item["snippet"]["label"])
                    return labels

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            #////// REPORT REASON SECONDARY REASON //////
            def get_video_abuse_report_reason_secondary_reasons(self, reason_id: str) -> (dict | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["snippet"]["secondaryReasons"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            def get_all_video_abuse_report_reason_secondary_reasons(self) -> (list[dict] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    reasons = []
                    for item in resources:
                        reasons.append(item["snippet"]["secondaryReasons"])
                    return reasons

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            #////// REPORT REASON SECONDARY REASON ID //////
            def get_video_abuse_report_reason_secondary_reason_id(self, reason_id: str) -> (dict | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["snippet"]["secondaryReasons"]["id"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            def get_all_video_abuse_report_reason_secondary_reason_ids(self) -> (list[str] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    ids = []
                    for item in resources:
                        ids.append(item["snippet"]["secondaryReasons"]["id"])
                    return ids

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            #////// REPORT REASON SECONDARY REASON LABEL //////
            def get_video_abuse_report_reason_secondary_reason_label(self, reason_id: str) -> (dict | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    for item in resources:
                        if item["id"] == reason_id:
                            return item["snippet"]["secondaryReasons"]["label"]
                        return None

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
            
            def get_all_video_abuse_report_reason_secondary_reason_labels(self) -> (list[str] | None):
                service = self.service

                try:
                    video = service.videoAbuseReportReasons().list(
                        part="snippet",
                    ).execute()

                    resources = video["items"]
                    labels = []
                    for item in resources:
                        labels.append(item["snippet"]["secondaryReasons"]["label"])
                    return labels

                except googleapiclient.errors.HttpError as e:
                    print(f"An API error occurred: {e}")
                    return None
                except IndexError as ie:
                    print(f"IndexError: Reason doesn't exist\n{ie}")
                    return None
                except TypeError as te:
                    print(f"Type error: You may have forgotten a required argument or passed the wrong type!\n{te}")
                    return None
                except KeyError as ke:
                    print(f"Key error: Bad key. Field doesn't exists!\n{ke}")
                    return None 
        
            