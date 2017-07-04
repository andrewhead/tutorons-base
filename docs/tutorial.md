# Make your own Tutoron

In this walkthrough, we will create a Tutoron that detects
and documents Java classes.  After following this tutorial,
you will be able to build Tutorons that detect and explain
arbitrary programming languages.  You will also be able to
integrate the explanations in arbitrary web pages.

A Tutoron can't run without a server to host it.  So before we start,
download and set up the Tutorons server by following the
instructions in the [getting started
guide](https://github.com/andrewhead/tutorons-base).  Follow
the guide to its conclusion, where you launch
a site on localhost.

## Create a server module for the Tutoron

### Make a Git repository for the Tutoron

All the code for your Tutoron should be stored in a separate
git repository from the server.  This lets future developers
add the Tutoron  to their servers if they want it, while not
requiring them to have it and its dependencies installed if
they don't want them.

Make a new Git repository on your favorite hosting
service.  For many people, this may mean [creating a new
free public
repository](https://help.github.com/articles/create-a-repo/)
on [GitHub](https://github.com/).

### Add the Tutoron to the server as a Git submodule

Say you created your Git repository at
`https://github.com/andrewhead/tutoron-java-classes.git`.
Now we'll mount your Tutoron as a server module
at `tutorons/modules/java_classes`:

```bash
# Assuming you're in the `tutorons-base` directory (the home directory of
# the Tutorons server) that you created in the getting started guide...
git submodule add \
  https://github.com/andrewhead/tutorons-java-classes.git \
  tutorons/modules/java_classes
```

### Initialize the Tutoron's source code

Create a Tutoron with boilerplate detection and explanation
code by running this command:

```bash
DJANGO_SETTINGS_MODULE=tutorons.settings.dev \
  python manage.py starttutoron java_classes
```

This generates about a dozen files with everything a
Tutoron needs: a code detector, code explainer,
templates for formatting the explanation as a tooltip, and
even unit tests.  All of this is written to files in
the `tutorons/modules/java_classes` directory you created
when you added the Git submodule for the Tutoron.
You'll touch most of these files as we tailor this Tutoron
to document Java classes.

### Integrate the Tutoron as a server "apps"

For the Tutorons server to find the Tutoron, we need
to do two things.  First, add the Tutoron as an "app" to the Django 
server by adding the following line to the list of 
`INSTALLED_APPS` in the `tutorons/settings/defaults.py` file:

```python
    'tutorons.modules.java_classes',
```

Second, point the Tutorons server to the URLs for the new
Tutoron.  You can do this by adding these two URL patterns
to the list of URL patterns in `tutorons/urls.py`:

```python
    url(r'^java_classes$', 'tutorons.modules.java_classes.views.scan', name='java_classes'),
    url(r'^java_classes/', include('tutorons.modules.java_classes.urls', namespace='java_classes')),
```

### Check that the Tutoron was integrated successfully

Make sure that the new Tutoron is working by running the
unit tests:

```bash
./runtests.sh
```

...and then by running the Tutoron on a web page!
Start the server:

```bash
./rundevserver.sh
```

Then, open http://localhost:8002/java_classes/example in
your browser.  You should be able to see that the Tutoron
currently detects and explains the variable `foo` in a
made-up language.  Neat!!

## Customize the Tutoron to document Java classes

Let's say we want to show snippets of documentation about Java
API classes whenever those classes show up on a
web page.  Let's tailor this Tutoron so that it
finds Java API classes and provides such documentation snippets.

For documentation, we'll use some example "insights" from
[Christoph Treude and Martin Robillard's
paper](https://ctreude.files.wordpress.com/2016/01/icse16a.pdf).
They automatically mined insightful sentences about Java API
members from posts on Stack Overflow—maybe they'll be useful
for people who look at Java tutorials on the web!

Let's create a Python list of dictionaries with these insights.
Each "insight" has the name of a class from the Java API and
an insightful sentence about that API.  Make a new file named
`tutorons/modules/java_classes/insights.py`. Paste this list
into that file:

```python
INSIGHTS = [
  {
    'class': 'ArrayList',
    'insight': "The list returned from asList has fixed size.",
  },
  {
    'class': 'LinkedList',
    'insight': "There is one common use case in which LinkedList " +
               "outperforms ArrayList: that of a queue.",
  },
]
```

In the next two steps, we'll *detect* all references
to Java API classes for which we have insights, and
then create *explanations* that a web page visitor can see
in a tooltip, attached to each reference.

### Write code to detect Java class mentions

Before we update the Tutoron's detection code to detect mentions
of Java classes, let's modify the detection test so that we
have some way to check if we implemented detection correctly.
Open up the current detection test at
`tutorons/modules/java_classes/tests/test_detect.py`.
Replace the existing `test_detect_foo` method with this
method:

```python
    def test_detect_java_builtin(self):

        html_doc = HtmlDocument('\n'.join([
            "<html>",
            "  <body>",
            "    <div>",
            "      <code>import java.util.ArrayList;</code>",
            "    </div>",
            "  </body>",
            "</html>",
        ]))
        code_regions = detect_code(html_doc)

        self.assertEqual(1, len(code_regions))
        code_region = code_regions[0]
        self.assertEqual("ArrayList", code_region.string)
        self.assertEqual("code", code_region.node.name)
        self.assertEqual(17, code_region.start_offset)
        self.assertEqual(25, code_region.end_offset)
```

The test case creates a fake HTML page with a code element
with a small line of Java code—`import
java.util.ArrayList;`.  The test checks the result of
detection (`detect_code`) on the HTML page: detection should
have yielded a single code region for the API member
`ArrayList`, at characters `17` to `25` within a `code` element.

We can see the new test fail when we run it:

```bash
./runtests.sh
```

Obviously, the test fails because we haven't yet implemented
the new detection logic.  To implement detection, open the
`tutorons/modules/java_classes/detect.py` file.  Look at the
current implementation: an "extractor" searches for the `pattern`
of the string `"foo"` in the text of an HTML element.  Every time it finds a
substring of text that matches the pattern, it records a "region" that
points to the position where the pattern was found.

We can reuse most of this code.  The only thing that's
different for us is that we want to look for several
patterns—one for each class in the `INSIGHTS` list.
The high-level strategy will be to loop over all entries
in the `INSIGHTS` list, create a set of patterns from the
class names in the list, and search for each pattern
(class name) one-by-one in the text.

Okay, let's implement detection of Java classes.  First,
we need access to the `INSIGHTS` data.  Beneath the current
imports in `tutoron/modules/java_classes/detect.py`, add
this import:

```python
from insights import INSIGHTS
```

Then, add code to create a set of patterns from the
classes in the list of insights.  Add this code before the
definition of the `JavaClassesExtractor` class:

```python
java_class_patterns = []

for insight in INSIGHTS:
    if insight['class'] not in java_class_patterns:
        java_class_patterns.append(insight['class'])
```

Finally, do a substring search on the text for
each pattern in `java_class_patterns`.  Replace the code
above the `while` loop (up through the `pattern = "foo"` line)
with this code:

```python

        # Initialize the list of regions outside of the for-loop: this list 
        # should contain regions found for *all* patterns.
        regions = []

        for pattern in java_class_patterns:
            
            # Reset pointer for substring match to the beginning of the text,
            # for each class.
            last_match_end = 0

            # The entirety of the `while True` loop will need to be indented
            # inside this for loop. The `return` statement should be outside of
            # the for loop.
            while True:
                ...

```

That's it!  Now run the tests again and we can see that detection works:

```bash
./runtests.sh
```

We have successfully implemented a detector for Java
classes!  This is good progress, though note that currently
the detector isn't that sophisticated and might yield false
positives.  See "Next Steps" for some pointers on building
more sophisticated detectors.

### Write code that provides documentation for Java classes

Now that we can detect Java classes, we need to write code that
maps a class to an explanation that can be shown
in a tooltip—in our case, an insight sentence.

Let's start with a test case that defines the expected
explanation behavior.  Open 
`tutorons/modules/java_classes/tests/test_explain.py` and
replace the test named `test_explain_that_foos_do_bar` with
this test:

```python
    def test_explain_ArrayList_with_insight(self):
        explanation = explain_code("ArrayList")
        self.assertIn("list returned from asList", explanation)
```

The test checks whether a string of code with the text 
`"ArrayList"` yields an explanation that contains a
substring of the expected insight sentence (`"list 
returned from asList"`).  This test should fail when 
we run it:

```bash
./runtests.sh
```

It's time to re-implement the code for making explanations
in the `explain_code` method of
`tutorons/modules/java_classes/views.py`.  Currently,
the method generates a single static explanation for
the word `"foo"`.  The method should instead give a custom
explanation for each class, comprising of one of the
insights from the list.

Import the `INSIGHTS` list into the `views.py` file by
adding this line below the rest of the imports:

```python
from insights import INSIGHTS
```

Then, create a custom explanation for each Java class by
replacing the code in the `explain_code` method with this:

```python
    for insight in INSIGHTS:
        if code_string == insight['class']:
            explanation = insight['insight']
            break
```

This code iterates over the list of insights, finds the
first insight that was written for the class, and sets
the explanation to that insight's text.

Run the tests again, and the Tutoron is now producing the
insights as explanations.

```bash
./runtests.sh
```

### Test the Tutoron on an example web page

We built a Tutoron that documents Java classes by
writing custom detection and explanation code.  But
how do we know it works?

Every Tutoron created with `starttutoron` has a test page
that can be used as an integration test.  Visit
http://localhost:8002/java_classes/example to see that page.
(*Reminder*: the server needs to be running, or else you
will see a "connection refused" error.  Run the server
with the `./rundevserver.sh` command.)

We need to update the test page, though: there are no
Java classes to explain on the web page yet!  So, we'll
add some Java classes to the code on the example page.  Open
`tutorons/modules/java_classes/templates/example.html`.
Then modify the content of the `<pre><code>` block.  That
line should look like this:

```html
            <pre><code>import java.util.ArrayList;</code></pre>
```

To see detection working, refresh the test page.  Did you
see `ArrayList` get highlighted?  And when you clicked on
it, did you see the tooltip that appeared, containing the
insight?  That's the explanation we wrote!

### Update the tooltip's HTML

*But wait*, you say. *Something's wrong.  The explanation
in the tooltip says, "You found the variable `ArrayList`,
and `ArrayList` is a Java class, not a variable!"*

You're right!  Up until now, I've left out one of the
important steps in explanation generation that we still
need to fix for the Java classes Tutoron.

We've already looked at the first step of explanation
creation.  The `explain_code` function is that first step.
It's written in Python because Python and APIs written in
Python provide useful utilities for looking up explanations
in databases and expressing complex logic for building up
English sentences and examples.

We're missing the second step.  In the second step,
the HTML of the tooltip body is rendered using the
`tutorons/modules/java_classes/templates/explanation.html` file.
The `explanation.html` template takes as input data passed (such
as a string or object representing an explanation of a piece
of code) from the `views.py` file, and formats it into the tooltip's HTML.
To fix this gaffe with calling `ArrayList` a variable, we
need to look at the part of the explanation that's created in
the second step in this template file.

Look at
`tutorons/modules/java_classes/templates/explanation.html`.
When this template is rendered, `{{ code_string }}` and `{{
explanation }}` will resolve to the text of the detected
code and the explanation generated by `explain_code`,
respectively.

The problematic explanation is in the first `p` element, 
where the initial template assumed that any explained
code would be for a variable.  We'll update this for our
Tutoron.  Replace the first `p` element with this line:

```html
<p>You found the Java class <code>{{ code_string }}</code>.</p>
```

Refresh the example page and see that the explanation
is now correct.

You may wonder, what part of the explanation do I put in
the `explain_code` method, and what part in the template?  Try
these rules of thumb: When part of an explanation
will be shared across all explanations, put that part of the
explanation in the template.  Any HTML formatting should
be done in the template.  Dynamically generated parts of
explanations should go in `explain_code`.  For additional tips
on generating HTML for explanations and code, see the
[Django docs about 
templates](https://docs.djangoproject.com/en/1.8/intro/tutorial03/#use-the-template-system).

## Integrating the Tutoron into web pages

Want to automatically detect and explain Java classes on
another web page?  Once you write your Tutoron, its
explanations can be made available for any page on the web,
with a couple of HTML additions.

First, you'll need to set up the Tutorons server (with your
module installed) on a server with a domain name and with
HTTPS communication enabled.  **You should absolutely enable
HTTPS and disable all HTTP communication to this server**.
A user's visit to the page and, depending on
the page, the way that page is rendered for them, can be
sensitive information.  You should respect this by making
sure all communication with your Tutorons server is
through HTTPS.

There are many options for setting up a Django server that
communicates over HTTPS.  DigitalOcean provides tutorials on
[serving Django apps with the Nginx reverse
proxy](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-16-04)
and [securing communication over Nginx with
HTTPS](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04).
When in doubt, ask someone with experience to help you with
setting up secure communication.  Feel free to send me a
message if you want pointers on how I did this for the
central Tutorons server.

Once you have launched your Tutorons server with a publicly
visible domain name, you can integrate your Tutoron
into any web page by adding these `<script>` tags to the
`<head>` of the page's HTML:

```html
        <script src="//tutorons.com/static/tutorons-library.js"></script>
        <script>
          document.addEventListener("DOMContentLoaded", function (event) {
            var tutoronsConnection = new tutorons.TutoronsConnection(window, {
              endpoints: {
                  java_classes: "//mydomain.com/java_classes",
              }
            });
            tutoronsConnection.scanDom();
          });
        </script>
```

Just replace `mydomain.com` with your domain name.  Then,
whenever someone opens the page, the `tutorons-library.js`
script will be fetched from the central Tutorons server to
load the Tutorons JavaScript API.  Once the page fully
loads, a call to `tutoronsConnection.scanDom()` uploads the
page contents to your Tutorons server, requesting code
detection and explanations.  Your server will
return a list of the detected code regions and their
explanations, which the Tutorons JavaScript API will
automatically attach to the web page.

## Show me the source code

Didn't follow this tutorial, but want to play around with
the result?  See the [finished source code for the
Tutoron](https://github.com/andrewhead/Tutoron-Java-Classes),
and follow the instructions in the source code's
README to test it out on a local server.

## Next Steps

### Improving detection

While this tutorial uses substring matching to detect
explainable code, sometimes it's useful to have more
accurate detection of code constructs.  For example,
if you wanted to explain `ArrayList` only when it was used
in a constructor, you would first want to extract the code
from a web page, run a parser over it, and traverse the
parse tree, looking only at tree nodes that belonged to a
constructor.  Many common languages have parsers implemented
in Python, or grammars that can be used with 
[ANTLR](http://www.antlr.org/) to
generate a parser.  When you look for such a parser, make
sure that it returns the character positions of all of the
nodes in the abstract syntax tree so you can recover the
exact character position of the matching code.

To get inspiration for more advanced parsing techniques,
see [this heavier version of the Tutorons
server](https://github.com/andrewhead/tutorons-server).

### Updating the tooltip style

If you want to modify the CSS style of the Tutorons, you
currently need to host your own version of the [Tutorons
library](https://github.com/andrewhead/tutorons-library).
Send us a message if you could use an easier way to
style your Tutorons.
