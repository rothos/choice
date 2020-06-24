import io
import re
import pdb
from markdown import markdown
from datetime import datetime

html = """
<html>
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <link rel="stylesheet" href="bootstrap.css">
    <link rel="stylesheet" href="jquery.ui.all.css">
    <link rel="stylesheet" href="jquery.tocify.css">
    <link rel='stylesheet' href='style.css'>
    <link href="https://fonts.googleapis.com/css?family=Lato:400,700&display=swap" rel="stylesheet">
</head>
<body>
    <div id='darkmode' class='lightmode'>toggle dark mode</div>
    <div id='hamburger'><div id='toc_open'>&#9776;</div></div>
    <div id="toc" class="lightmode"><div id='toc_close' class="lightmode"><span>&times;</span></div></div>
    <div id='content'>%s</div>

    <script src="jquery-1.8.3.min.js"></script>
    <script src="jquery-ui-1.9.1.custom.min.js"></script>
    <script src="bootstrap.js"></script>
    <script src="jquery.tocify.js"></script>
    <script src="smartquotes.js"></script>
    <script>smartquotes();</script>
    <script type='text/javascript'>
        $(function() {
            //Calls the tocify method on your HTML div.
            $("#toc").tocify({
                "selectors": "h2,h3,h4,h5,h6",
                "extendPage": false
            });
        });
    </script>
    <script type='text/javascript'>
        $(document).ready(function() {
            $('#darkmode').click(function(){
                $('body').toggleClass('darkmode')
                $('.alert').toggleClass('darkmode')
                $('#toc').toggleClass('darkmode')
                $('#toc_close').toggleClass('darkmode')
                $('#hamburger').toggleClass('darkmode')
                $('#darkmode').toggleClass('darkmode')
            })

            $('#toc_open').click(function(){
                $('#toc').toggleClass('show')
            })
            $('#toc_close').click(function(){
                $('#toc').toggleClass('show')
            })
        })
    </script>
    <script async src="https://www.googletagmanager.com/gtag/js?id=UA-96730045-1"></script>
    <script> window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'UA-96730045-1');</script>
</body>
</html>
"""

infile = io.open('index.md', mode='r', encoding='utf-8')
text = infile.read()

# Process the footnotes.
index = 1
locations = []
replacements = []
footnotes = []

# Here is our regex, matching both footnotes and footnote section tags.
exp = re.compile('(\[\[.*?\]\]|\{\{footnotes\}\})')
matches = exp.finditer(text)

# Loop through each of the matches.
for m in matches:
    locations += [m.span()]
    match_string = m.group()

    # This is a footnote section.
    # Collect all the footnotes up to this point, flush them out
    # into a section.
    if match_string == '{{footnotes}}':
        ol = "<ol class='footnotes' start=%i>\n%s\n</ol>"
        make_li = lambda i,s: "<li id='footnote-%.3i'>%s</li>" % (i, s)

        initial_index = footnotes[0][0]
        li_str = "\n".join([make_li(i,s) for (i,s) in footnotes])

        replacements += [ol % (initial_index, li_str)]
        footnotes = []

    # This is a footnote.
    else:
        replacements += \
            ["<a class='footnote' href='#footnote-%.3i'>[%i]</a>" \
                % (index, index)]
        footnotes += [(index, match_string[2:-2])]
        index += 1

# Do all the replacements.
replace_substr = lambda loc,string,rep: string[:loc[0]] + rep + string[loc[1]:]
for i in reversed(range(len(locations))):
    loc = locations[i]
    rep = replacements[i]
    text = replace_substr(loc, text, rep)

rendered_text = markdown(text).encode('utf-8')
infile.close()

rendered_text = rendered_text.replace('%%DATE%%',
    datetime.utcnow().strftime('%Y-%m-%d-%H:%M:%S')+" UTC")

outfile = open('index.html', 'w')
outfile.write(html % rendered_text)
outfile.close()
