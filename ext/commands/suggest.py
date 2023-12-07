import interactions
import uuid
from common.models import EMBEDDED_MESSAGE
import datetime
from common.consts import METADATA

"""
This extension integrates a slash command to create suggestions.

__Purpose:__ Receive the \"suggest\" application command context from the user and process it. Following this 
it responds to the user with a modal to create the suggestion desired.

__Utilizes:__ modal_worker.py && component_worker.py
"""


class Suggestion(interactions.Extension):
    def __init__(self, bot: interactions.Client):
        self.set_extension_error(self.error_handler)
        
    @interactions.slash_command(description="Suggest something to the server.",
                                scopes=METADATA["guilds"])
    async def suggest(self, ctx: interactions.SlashContext):
        
        # Unique identifier for the suggestion on the database
        # Stored in embed footer as well for easy access
        SUGGESTION_ID = str(uuid.uuid4())
            
        suggestion_modal = interactions.Modal(
            interactions.ShortText(label="Title", 
                                   placeholder="Suggestion title", 
                                   custom_id="title"),
            interactions.ParagraphText(label="Description", 
                                       placeholder="Suggestion details", 
                                       custom_id="description"),
            title="Create a Suggestion",
            custom_id=f"suggestion?{SUGGESTION_ID}",
        )
        
        emojis = ["👍", "👎"]
        
        # Attachment needs to be specified as "None" due to library limitations, it was either that or a blank string
        await EMBEDDED_MESSAGE(uuid=SUGGESTION_ID,
                               counts={emoji: 0 for emoji in emojis},
                               user_ids={},
                               created_at=datetime.datetime.utcnow(),
                               author_id=str(ctx.author.id),
                               attachment="None",
                               ).create()
            
        """
        After the modal is sent the actions take place in the following order:
        ext.listeners.modal_worker.py -> ext.listeners.component_worker.py
        """
        await ctx.send_modal(modal=suggestion_modal)
        
    async def error_handler(self, error: Exception, ctx: interactions.BaseContext, *args, **kwargs):
        match error.status:
            case 404:
                await ctx.send(f"Interaction timed out.", ephemeral=True)
                return
                
        raise(error)