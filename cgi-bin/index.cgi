#!/usr/bin/perl -w
#
# index.cgi
#
# This file is part of CGIndex.
# https://github.com/userbrett/cgindex
#
# This CGI is used to overrides Apache's autoindex module.
#
# To use this file, put it in /cgi-bin add it to the end of the
# Apache's DirectoryIndex parameter.
#
# Example:
# DirectoryIndex   index.html index.shtml index.html /cgi-bin/index.cgi
#
# ###########################################################################


use strict;
use diagnostics;
use CGI::Carp();
use CGI qw(-compile :all);
use File::Basename;
use Switch;



# While you may map all of your files under the DOCUMENT_ROOT, that may make
# the locations confusing - say, when they are mounted via NFS and the NFS
# server uses one mount point for them and the webserver has them mounted
# elsewhere.  To help with that, a hash table can be created to map from one
# filesystem path to another URI path.
#
my ( %alias_doc_roots,  # mappings between filesystem path and REQUEST_URI path
     $uri_root,         # the first directory in the REQUEST_URI
     $real_dir,         # the directory on the filesystem to display
     @dirlist,          # entire set of items in the directory to display
     $diritem,          # just one of the files/directories in the directory to display
     $itemname,         # actual file *OR* directory name - no path info
     $path,             # the path info for $itemname
     @filepart,         # parts of $itemname (basename, extension)
     $icon,             # type of icon to display (depends on extension
     $debug);           # 1 for debug, 0 for not


$debug = 0;


# Configure all aliased paths here.
#
# The alias (left side) references the real path ($alias => $realpath)
# For example, if:
#
# 1) you have photos under /nfs/photos/ references by the alias "/photos",
# and
# 2) you have songs under /nfs/music/songs referenced by the alias "/songs",
#
# then you would configure this as follows:
#
#   %alias_doc_roots = (
#      'photos'    => '/nfs/photos',
#      'songs'     => '/nfs/music/songs'
#   );
#
%alias_doc_roots = (
  'pub'          => '/data/webdocs/etpenguin/pub',
  'local_icons'  => '/var/www/local_icons',
  'index_icons'  => '/var/www/index_icons',
  'icons'        => '/var/www/icons'
);

#%alias_doc_roots = (
#  'photos'       => '/data/photos',
#  'pub'          => '/data/webdocs/brettlee/pub'
#);

$debug && print "DOCUMENT_ROOT:  " . $ENV{DOCUMENT_ROOT} . "<br>";
$debug && print "REQUEST_URI:  " . $ENV{REQUEST_URI} . "<br>";




# Parse out the root of the REQUEST_URI to see if it matches
# within %alias_doc_roots.
#
if ( $ENV{REQUEST_URI} =~ m|/(.+?)/(.*)| ) {
  $uri_root = $1;
}
$debug && print "Root of the REQUEST_URI:  " . $uri_root . "<br>";




# Check to see if the REQUEST_URI contains an alias defined
# in %alias_doc_roots.  If so, switch the mapping from the URI request path to
# the filesystem path.
#
if ( $alias_doc_roots{$uri_root} ) {
  $real_dir = $alias_doc_roots{$uri_root}; 
  $debug && print "This is an aliased URI.<br>The filesystem path is:  $real_dir <br>";
  $real_dir =~ s|/$uri_root||;
  $real_dir .= $ENV{REQUEST_URI};
  $debug && print "The filesystem URI is:  $real_dir <br>";
#
# The request is not for an aliased path, so use the standard doc root.
#
} else {
  $real_dir = $ENV{DOCUMENT_ROOT} .  $ENV{REQUEST_URI};
}



# HTML-ify the $real_dir variable to transition from URI to filesystem.
# (whitespace, quotes, etc.)
#
$real_dir =~ s/%20/ /g;
$real_dir =~ s/%27/'/g;
$real_dir =~ s/(\s)/\\$1/g;


# HTML-ify the $REQUEST_URI variable to transition from URI to filesystem.
#
$ENV{REQUEST_URI} =~ s/%20/ /g;
$ENV{REQUEST_URI} =~ s/%27/'/g;



# Generate a fully-pathed list of files for the request.
#
@dirlist = < $real_dir* >;




# Generate the page.
#
# In this case, we've setup a static filename "cgi.header" which
# contains the beginning HTML.
#


print header;


if (open (FILE, "$ENV{DOCUMENT_ROOT}/cgi.header" )) {
  while (<FILE>) {
    print;
  }
  close FILE;
};


print "Directory Listing For: " . $ENV{REQUEST_URI} . "<br><br>";

print "<table>";




# Provide a link to the directory one level up.
#
# Using the Windows XP icons.
# Better would be to detect the OS and use the appropriate set.
#
print "<tr><td><a href='..'
       class=headingL><img src=/index_icons/winxp/back.png
       border=0>&nbsp;Parent Directory</a><br><br></td></tr>";



# Looping through the directory items...
# This is loop 1 of 2.  It handles directories.
#
foreach $diritem ( @dirlist ) {

  # handle directories
  #
  if ( -d $diritem ) {

    # split into link (file or directory) and path
    ( $itemname, $path) = fileparse( $diritem );
    $icon = "dir";

    # Escape single quotes
    $itemname=~ s/'/\'/;

    # Reset URI to http for creating valid links
    $ENV{REQUEST_URI} =~ s/ /%20/g;
    $ENV{REQUEST_URI} =~ s/'/%27/g;

    # Do not display these files or directories in the directory listing
    # Note: thumbnails is a special directory name that can contain thumbnails of photos
    # to be displayed alongside the photo filename for easier browsing of the photos
    #
    if (! ( $itemname =~ m/thumbnails/ )) {

      print "<tr><td><a href=\"$itemname\"
             class=headingL><img src=/index_icons/winxp/$icon.png
             border=0>&nbsp;$itemname</a></td></tr>";
    }
  }
}



# Looping through the directory items...
# This is loop 2 of 2.  It handles files.
#
foreach $diritem ( @dirlist ) {

  # handle files
  #
  if ( -f $diritem ) {

    # split into link (file or directory) and path
    ( $itemname, $path ) = fileparse( $diritem );


    # find the filename extension, if it exists
    @filepart = split( '\.', $diritem );


    # if no filename extension
    if (! $filepart[@filepart-1] ) {
      $icon = "unknown";


    # if extension matches, use an appropriate icon
    } else {

      switch (  lc($filepart[@filepart-1])  ) {

          case "bmp"   { $icon = "image"; }
          case "class" { $icon = "java"; }
          case "conf"  { $icon = "text"; }
          case "doc"   { $icon = "doc"; }
          case "docx"  { $icon = "doc"; }
          case "gif"   { $icon = "image"; }
          case "gz"    { $icon = "compressed"; }
          case "htm"   { $icon = "web"; }
          case "html"  { $icon = "web"; }
          case "jar"   { $icon = "java"; }
          case "java"  { $icon = "java"; }
          case "jpg"   { $icon = "image"; }
          case "js"    { $icon = "js"; }
          case "key"   { $icon = "key"; }
          case "ods"   { $icon = "xls"; }
          case "odt"   { $icon = "doc"; }
          case "pdf"   { $icon = "pdf"; }
          case "php"   { $icon = "php"; }
          case "png"   { $icon = "image"; }
          case "ppt"   { $icon = "ppt"; }
          case "pptx"  { $icon = "ppt"; }
          case "ps"    { $icon = "ps"; }
          case "rtf"   { $icon = "doc"; }
          case "tar"   { $icon = "compressed"; }
          case "tif"   { $icon = "image"; }
          case "txt"   { $icon = "text"; }
          case "tgz"   { $icon = "compressed"; }
          case "vsd"   { $icon = "visio"; }
          case "wav"   { $icon = "sound"; }
          case "xls"   { $icon = "xls"; }
          case "zip"   { $icon = "compressed"; }
          else         { $icon = "unknown"; }
      }
    }


    # Escape single quotes.
    $itemname=~ s/'/\'/;

    # Revert REQUEST_URI to create valid links.
    $ENV{REQUEST_URI} =~ s/ /%20/g;
    $ENV{REQUEST_URI} =~ s/'/%27/g;


    # Begin content display...


    # Never display these types of files.
    if (! (
            ( $itemname =~ m/TABAFK/ )
         || ( $itemname =~ m/Thumbs.db/ ) 
         || ( $itemname =~ m/(\.a$)/i )
         || ( $itemname =~ m/(\.bin$)/i )
         || ( $itemname =~ m/(\.class$)/i )
         || ( $itemname =~ m/(\.cer$)/i )
         || ( $itemname =~ m/(\.ear$)/i )
         || ( $itemname =~ m/(\.exe$)/i )
         || ( $itemname =~ m/(\.jar$)/i )
         || ( $itemname =~ m/(\.gz$)/i )
         || ( $itemname =~ m/(\.o$)/i )
         || ( $itemname =~ m/(\.rpm$)/i )
         || ( $itemname =~ m/(\.tar$)/i )
         || ( $itemname =~ m/(\.tgz$)/i )
         || ( $itemname =~ m/(\.war$)/i )
         || ( $itemname =~ m/(\.zip$)/i )
       ) )
    {

      if ( -e "$path/thumbnails/$itemname" ) {

        # If a thumbnail exists, display it.
        print "<tr><td><a href=\"$itemname\" class=headingL><img
               src=\"$ENV{REQUEST_URI}/thumbnails/$itemname\"
               border=0></a>&nbsp;<a href=\"$itemname\"
               class=headingL>$itemname</a></td></tr>";


      # These files are "browser associated".
      # Meaning, it will not be printed, but it will directly linked
      # thus allowing the browser associations to handle the file.
      } elsif (
           ( $itemname =~ m/(\.db$)/i )
        || ( $itemname =~ m/(\.dd$)/i )
        || ( $itemname =~ m/(\.doc$)/i )
        || ( $itemname =~ m/(\.docx)/i )
        || ( $itemname =~ m/(\.eps)/i )
        || ( $itemname =~ m/(\.fig)/i )
        || ( $itemname =~ m/(\.img$)/i )
        || ( $itemname =~ m/(\.gif$)/i )
        || ( $itemname =~ m/(\.ico$)/i )
        || ( $itemname =~ m/(\.iso$)/i )
        || ( $itemname =~ m/(\.jpg$)/i )
        || ( $itemname =~ m/(\.jks$)/i )
        || ( $itemname =~ m/(\.jpeg$)/i )
        || ( $itemname =~ m/(\.mov$)/i )
        || ( $itemname =~ m/(\.mpg$)/i )
        || ( $itemname =~ m/(\.pdf$)/i )
        || ( $itemname =~ m/(\.png$)/i )
        || ( $itemname =~ m/(\.ppt$)/i )
        || ( $itemname =~ m/(\.pptx$)/i )
        || ( $itemname =~ m/(\.ps$)/i )
        || ( $itemname =~ m/(\.rtf$)/i )
        || ( $itemname =~ m/(\.vsd$)/i )
        || ( $itemname =~ m/(\.xls$)/i )
        || ( $itemname =~ m/(\.xlsx$)/i )
        || ( $itemname =~ m/(\.xsd$)/i )
        || ( $itemname =~ m/(\.xsl$)/i )
        )
      {

        # Provide a direct link to the file.
        print "<tr><td><a href=\"$ENV{REQUEST_URI}$itemname\"
               class=headingL><img src=/index_icons/winxp/$icon.png
               border=0>&nbsp;$itemname</a></td></tr>";

      } else {

        # These files "should be" text files that can be displayed inline.
        print "<tr><td><a href=\"/cgi-bin/showfile.cgi?$ENV{REQUEST_URI}$itemname\"
               class=headingL><img src=/index_icons/winxp/$icon.png
               border=0>&nbsp;$itemname</a></td></tr>";
      }
    }
  }
}

print "<tr><td><div class=headingL><br><br><i><a 
       href=\"https://github.com/userbrett/cgindex\"
       class=headingL>Directory listings generated by CGIndex</a>
       </i></div></td></tr></table>";



#
# End display of the HTML page
#
# In this case, we've setup a static filename "cgi.footer" which
# contains the endingHTML.
#
# ------------------------------------------------------------------

if (open (FILE, "$ENV{DOCUMENT_ROOT}/cgi.footer" )) {
  while (<FILE>) {
    print;
  }
  close FILE;
};



# 
# END
# ------------------------------------------------------------------


