# Making your own Tutoron

In this walkthrough, you will create a Tutoron that detects
and documents Java classes.  After following this tutorial,
you will be able to build Tutorons that detect and explain
arbitrary programming languages, and you will be able to
integrate them into arbitrary web pages.  Let's begin!

## Create scaffolding for the new Tutoron

A Tutoron can't run without a server to host it.  So first,
download and set up the base Tutorons server by following the
instructions in the [getting started
guide](https://github.com/andrewhead/tutorons-base).  Make
sure to follow the guide to its conclusion (where you launch
a site on localhost).

### Create a git repository for your Tutoron

All the code for your Tutoron will be stored in a separate
git repository.  This will let people add your Tutoron as a
submodule to their project if they want it.

Create a new git repository on your favorite hosting
service.  For most people, this will mean [creating a new
free public
repository](https://help.github.com/articles/create-a-repo/)
on [GitHub](github.com/).

### Add your Tutoron as a submodule to the server

Let's say you set up your git repository at
`https://github.com/andrewhead/tutoron-java-classes.git`.
Remember the `tutorons-base` directory you created in the
getting started guide?  Now we'll mount your Tutoron as a
module into the server, as the `java_classes` directory.
Like so:

```bash
cd tutorons-base/modules
git submodule add \
  https://github.com/andrewhead/tutorons-java-classes.git \
  java_classes
```

### Initialize the source code for the Tutoron

You can run a convenience command to create the
files needed for any Tutoron.

```bash
cd ..  # Back to the tutorons-base directory
DJANGO_SETTINGS_MODULE=tutorons.settings.dev \
  python manage.py starttutoron java_classes
```

This generates about a dozen files that have everything a
Tutoron needs: a basic code detector, code explainer,
templates for formatting the explanation as a tooltip, and
even working unit tests.  All of this is written to files in
the `tutorons/modules/java_classes` directory.
In the upcoming steps, we'll be tailoring these files so
that they detect Java in a webpage and look up an
explanation.  For the time being, the following files have
been created in the `modules/java_classes` directory:

* `views.py`: methods for generating explanations of code
  given a webpage, or a small selection of text
* `urls.py`: patterns pointing from partial URL paths to the
  views that create the explanations
* `tests/`: a directory containing starter code for unit
  tests for checking the logic of the Tutoron
* `templates/explanation.html`: when rendered, this
  template will become the HTML inserted in a tooltip to
  explain a detected piece of code

### Integrate your Tutoron as one of the server's "apps"

For the Tutorons server to be able to find your app, we need
to do two things.: Add the Tutoron as an "app" to the Django 
server by adding the following line to the list of 
`INSTALLED_APPS` in the `tutorons/settings/defaults.py` file:

```python
    'tutorons.modules.java_classes',
```

Point the Tutorons server to the URLs from the new
Tutoron.  You can do this by adding these two URL patterns
to the list of URL patterns in `tutorons/urls.py`:

```python
    url(r'^java_classes$', 'tutorons.modules.java_classes.views.scan', name='java_classes'),
    url(r'^java_classes/', include('tutorons.modules.java_classes.urls', namespace='java_classes')),
```

### Check that the installation was successful

Make sure that the new Tutoron is working by running the
unit tests:

```bash
./runtests.sh
```

Let's see the starter Tutoron in action.  Start the server:

```bash
./rundevserver.sh
```

Then go to http://localhost:8002/java_classes/example in
your browser.  The base Tutoron that has been created for
you detects and explains the variable `foo` in a
non-existent language on this page.

Now you have a minimal working Tutoron.  The next step is to
write a detector and explainer for your language.  We'll
cover that process in a dedicated tutorial soon.

## Program the Tutoron to show insights about Java classes

Let's say I have a database of insights about common members
of the Java API that I want to make available to programmers
when they're looking through some online learning materials.
In this case, the insights are examples from [Christoph
Treude and Martin Robillard's
paper](https://ctreude.files.wordpress.com/2016/01/icse16a.pdf)
on extracting insightful clarifying sentences about API
members from posts on Stack Overflow.

The insights are currently in a Python list of dictionaries.
Each "insight" has the name of a class from the Java API and
an insightful sentence about that API:

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

Make a new file names `insights.py` in the
`tutorons/modules/java_classes/` directory.  Paste the
dictionary above into the `insights.py` file.

The next two steps will be to *detect* all code that refers
to these API members, and then *explain* each API member
that gets found.

### Detecting Java code

Start by modifying the detection test.  We'll use this test
check that our detection was correctly implemented.  Open up
the detection test at
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

This test case creates a fake HTML page with a code element
that contains a small line of Java code—`import
java.util.ArrayList;`.  The test checks on the result of
running detection (`detect_code`) on the HTML page: it
should have found a code region for the API member
`ArrayList` at characters `17` to `25` in a `code` element.

See the new test fail when you run it:

```bash
./runtests.sh
```

The test fails because we haven't yet implemented the logic
that detects Java classes.  Open the
`tutorons/modules/java_classes/detect.py` file and modify
the detection logic.  The detection logic is already mostly
there in the generated code: it searches for the `pattern`
of the string `"foo"` in the text.  Every time it finds a
substring that matches the pattern, it creates a "region"
with the text of the pattern that was found and the position
of the pattern within the text.

The only thing that's different for us is that we want to
look for several different patterns instead of just one—we
need to detect both `ArrayList` and `LinkedList`.  More
generally, we want to detect all classes for which there's
an insight in the `INSIGHTS` list.

Our high-level strategy will be to iterate over all insights
in the `INSIGHTS` list, create a list of patterns from the
class names in the list, and search for each pattern one at
a time.

Let's implement detection of Java classes.  First, we need
access to the `INSIGHTS` data.  Beneath the rest of the
imports in `tutoron/modules/java_classes/detect.py`, add
this import:

```python
from insights import INSIGHTS
```

Then, add code that creates a list of patterns from the
classes in the list of insights.  Add the code before the
definition of the `JavaClassesExtractor` class:

```python
java_class_patterns = []

for insight in INSIGHTS:
    if insight['class'] not in java_class_patterns:
        java_class_patterns.append(insight['class'])
```

Finally, we need to do a substring search on the text for
all patterns in `java_class_patterns`.  Replace the code
above the `while` loop (up through the `pattern = "foo"` line)
with the following code:

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

That's it!  Now run the tests again and see them pass:

```bash
./runtests.sh
```

We have successfully implemented a detector for Java
classes!  This is good progress, though note that currently
the detector isn't that sophisticated and might yield false
positives.  See "Next Steps" for some pointers on building
more sophisticated detectors.

### Explaining Java code

Now we need to program the Tutoron to show insight sentences
for a class.

We'll start by writing another test.  Open up
`tutorons/modules/java_classes/tests/test_explain.py`.
Replace the test names `test_explain_that_foos_do_bar` with
the following test:

```python
    def test_explain_ArrayList_with_insight(self):
        explanation = explain_code("ArrayList")
        self.assertIn("list returned from asList", explanation)
```

This test checks to see whether an explanation of code with
the text `"ArrayList"` contains a substring from the insight
for this API member (`"list returned from asList"`).

Like before, you should see the test fail after adding the
test case:

```bash
./runtests.sh
```

Look at the current logic for explaining code in the
`explain_code` method of the
`tutorons/modules/java_classes/views.py` file.  Currently,
the method generates a single explanation—an explanation of
the word `"foo"`.  Let's instead provide a custom
explanation for each class, comprising of one of the
insights from our list.

Import the `INSIGHTS` list by adding this line below the
rest of the import statements:

```python
from insights import INSIGHTS
```

Then, provide a custom explanation of each Java class by
replacing the body of the `explain_code` method with this
code:

```python
    for insight in INSIGHTS:
        if code_string == insight['class']:
            explanation = insight['insight']
            break
```

This code iterates over the list of insights, finds the
first insight that was written for the class by comparing
the `code_string` of a detected region to the insight's
class name, and sets the explanation to that insight's text.

Run the tests again, and the Tutoron is now producing the
insights as explanations!

```bash
./runtests.sh
```

Mapping detected code to pre-written explanations will
be enough for many Tutorons.  If you're interested in
experimenting with more complex explanation generation,
see the notes in "Next Steps".

### Testing the Tutoron out on a web page

We built a complete Tutoron by providing custom detection
and explanation code.  But how do we know it works?

Every Tutoron created with `starttutoron` has a test page
that you can use as an integration test to make sure that
detection, explanation, and the rest of the server is
working correctly.  Visit
http://localhost:8002/java_classes/example to see this page.

But there's a problem: there are no Java classes to explain
on this web page!  We need to add some Java classes so we
can make sure detection is working.

So, we'll add some Java classes to the code on this example
page.  Open
`tutorons/modules/java_classes/templates/example.html`.
Then modify the content of the `<pre><code>` block.  When
you're finished, the line should look like this:

```html
            <pre><code>import java.util.ArrayList;</code></pre>
```

To see detection working, refresh the test page.  Did you
see `ArrayList` get highlighted?  And when you clicked on
it, did you see the tooltip that appeared, containing the
insight?  That's the explanation we wrote!

### Adjusting the tooltip HTML

*But wait, the explanation says "You found the variable
`ArrayList`, and that's not right*.  `ArrayList` is a Java
class, and not a variable.

Okay, you caught me.  Explanation is actually split across
two places, and we have only modified the explanation in one
of these two places.

We've already looked at the first step of explanation
creation.  The `explain_code` function is that first step.
It's written in Python because Python and APIs written in
Python provide useful utilities for looking up explanations
in databases and expressing complex logic for building up
English sentences and examples.

In the second step, the HTML of the tooltip body is rendered
using the
`tutorons/modules/java_classes/templates/example.html` file.
The `example.html` template takes as input data passed (such
as a string or object representing an explanation of a piece
of code) from the `views.py` file, and formats it as HTML.
To fix this gaffe with calling `ArrayList` a variable, we
need to look at the part of the explanation that's created in
the second step.

Look at
`tutorons/modules/java_classes_templates/example.html`.
When this template is rendered, `{{ code_string }}` and `{{
explanation }}` will resolve to the text of the detected
code and the explanation generated by `explain_code`,
respectively.

The problem is with the first `p` element, where it was
assumed that any explained code would be for a variable.
We'll update this for our Tutoron, where we're providing
insights about Java classes.  Replace the first `p` element
with this line:

```html
<p>You found the Java class <code>{{ code_string }}</code>.</p>
```

Refresh the example page.  The explanation is now correct!

You may wonder, how do we know whether to put description
into the `explain_code` method, or the template?  I
recommend these rules of thumb: When part of an explanation
will be shared across all explanations, put that part of the
explanation in the template.  Any HTML formatting should
be done in the template.  Dynamically generated parts of
explanations should go in `explain_code`.

## Integrating the Tutoron into other web pages

Want to automatically detect and explain Java classes on
another web page?  Once you write your Tutoron, its
explanations can be made available across the web.

The first step is to set up the Tutorons server, with your
module installed, on a server with a domain name and with
HTTPS communication enabled.  **You should absolutely use
HTTPS and disable all HTTP communication to this server**.
In the current code for Tutorons, a user uploads their page
to the server.  A user's visit to the page and, depending on
the page, the way that page is rendered for them, can be
very sensitive information.  You should respect this by
making sure all communication with your Tutorons server is
over HTTPS.

There are many options for setting up a Django server that
communicates over HTTPS.  DigitalOcean offers tutorials on
[serving Django apps over
Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-16-04)
and [securing communication with
HTTPS](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04).
When in doubt, ask someone with experience to help you with
setting up secure communication.  Feel free to send me a
message if you want pointers on how I did this for the
central Tutorons server.

Once you have done this, you can integrate your Tutoron
with any page by adding these `<script>` tags to the
`<head>` of a page's HTML:

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
detection and explanations.

## Show me the source code

Want to look at the code you would have written if you had
followed this tutorial?  It's online at
https://github.com/andrewhead/Tutoron-Java-Classes.  To test
out this code, follow the instructions in the README for
that repository.

## Next Steps

### Improving detection

While this tutorial uses substring matching to detect
explainable code, sometimes it's useful to locate
explainable code by traversing a parse tree.  For example,
if you wanted to explain `ArrayList` only when it was used
in a constructor, you would first want to extract the code
from a web page, run a parser over it, and traverse the
parse tree, looking only at tree nodes that belonged to a
constructor.  Many common languages have parsers implemented
in Python, or a grammar that can be used with ANTLR to
generate a parser.  When looking for such a parser, make
sure that it preserves the character positions of all of the
nodes in the abstract syntax tree so you can recover the
exact character position of the matching code.

### Updating the tooltip style

If you want to modify the CSS style of the Tutorons, you
currently need to host your own version of the [Tutorons
library](https://github.com/andrewhead/tutorons-library).
