from jinja2 import Environment, BaseLoader, ChoiceLoader, TemplateNotFound
from uuid import uuid4, SafeUUID

try:
    from flask import Flask
except ImportError:
    class Flask:
        pass

class PageLoader(BaseLoader):
    """
    A dummy jinja2 loader to intercept template requests and use a string instead.
    Without this, jinja2 does not support {% extend %} on strings.
    Used by Page - should not be used elsewhere.
    """

    pages = {}

    def get_source(self, env: Environment, name: str) -> tuple[str, str, bool] | None:
        """
        If the requested template name begins with '@page:', returns the template from the pages dictionary.
        Otherwise, allows a second loader (using jinja2.ChoiceLoader) to handle the template.
        """
        
        if name[:6] == "@page:":
            return self.pages[name[6:]], name, True
        else:
            raise TemplateNotFound(name)

    def create_store(self, uuid: str, content:str):
        """
        Create an item in the 'pages' dictionary. Uses the UUID passed to reference it.
        The page can be retrieved as a jinja2.Template object by calling jinja2.Environment.get_template() with argument '@page:' followed by the UUID.
        """

        self.pages[uuid] = content
    
    def recycle(self, uuid: str):
        """
        Deletes a page from the 'pages' dictionary. Call after a page has been rendered.
        """
        del self.pages[uuid]


class Page:
    """
    Creates a Page object that blocks can be added to.
    These blocks are turned into a jinja template on render which extends another template.
    Should be used through Formatter() - not to set up an environment.
    """

    _blocks = {}

    def __init__(self, template: str, env: Environment, blockloader: BaseLoader):
        """
        Sets up the page with a template and loaders.
        Creates a PageLoader and a jinja2 environment with a ChoiceLoader to choose between the PageLoader and the default template loader. 
        Uses the blockloader loader to get block files, but does not add this to the environment so that the render function can use this to get block files.
        """

        self.template = template
        self.env = env
        self.blockloader = blockloader
        self.pageloader = self.env.loader.loaders[0]

        self.uuid = uuid4().hex
        self.page = ""

    def add_block(self, name: str, file: str):
        """
        Adds the contents of a file to a the page.
        Renders within a jinja {% block %} tag to extend another template.
        """

        block, _, _ = self.blockloader.get_source(self.env, file)
        self._blocks[name] = "\n".join(block.split("\n")[1:])
    
    def render(self, **args):
        """
        Renders the page using jinja2.
        Adds the template and the blocks to the PageLoader, then uses jinja to render the page by extending another template.
        """

        self.page += "{% extends '"
        self.page += self.template
        self.page += "' %}\n"

        for block in self._blocks:
            self.page += "{% block "
            self.page += block
            self.page += " %}\n"
            self.page += self._blocks[block]
            self.page += "{% endblock %}\n"

        self.pageloader.create_store(self.uuid, self.page)
        render = self.env.get_template("@page:" + self.uuid)

        return render.render(args)

class Formatter:
    """
    Class to set up a formatter from a jinja2 Environment or a flask Flask app.
    """

    def __init__(self, instance: Environment | Flask, blockloader: BaseLoader | None=None):
        """
        Sets up the formatter with a jinja2 environment that includes a ChoiceLoader to allow the PageLoader to intercept requests to '@page' before deferring to the default envionment loader.
        If using flask, the jinja environment must be set up before this is registered - as this accesses the Flask.jinja_env variable, any changes made tojinja_option afterwards will have no effect.
        The blockloader argument is required for setup from a jinja2 environment. If setting up from a Flask instance, the blockloader can instead be configured from Flask.config. 
        """

        if isinstance(instance, Environment):
            env = instance
        elif isinstance(instance, Flask):
            env = instance.jinja_env
            if not blockloader and "FORMATTER_BLOCK_LOADER" in instance.config:
                blockloader = instance.config["FORMATTER_BLOCK_LOADER"]
        else:
            raise TypeError("Unrecognised instance - cannot generate environment.")
    
        if not blockloader:
            raise AttributeError("No loader defined for blocks.")

        self.pageloader = PageLoader()
        self.env = env.overlay(loader=ChoiceLoader([self.pageloader, env.loader]))
        self.blockloader = blockloader

    def create_page(self, template: str) -> Page:
        """
        Wrapper function to create a Page object using the registered Environment.
        """

        return Page(template, self.env, self.blockloader)

if uuid4().is_safe == SafeUUID.unsafe:
    print("UUIDs generated are not thread-safe. Proceed with caution and do not use multithreading.")
elif uuid4().is_safe == SafeUUID.unknown:
    print("UUIDs generated may not be thread-safe. Proceed with caution and do not use multithreading.")