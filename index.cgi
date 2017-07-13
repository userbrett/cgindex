#!/usr/bin/env perl
#
# This script, index.cgi, is used to generate autoindex's.  It does not
# use Apache's autoindex module.  Instead, it uses Apache's DirectoryIndex
# parameter.
#
# Put this script in /cgi-bin and add "/cgi-bin/index.cgi" to Apache's
# DirectoryIndex parameter.
#
# Example:
# DirectoryIndex   index.html index.shtml index.htm /cgi-bin/index.cgi
#
# If you have any aliased directories, you will need to configure them
# below using the variable "%alias_doc_roots."
#


use strict;
use warnings;
use diagnostics;
use CGI::Carp();
use CGI qw(-compile :all);
use File::Basename;
use Switch;


my ( %alias_doc_roots,  # for any aliased DOCUMENT_ROOT's
     $uri_root,         # the root path of the REQUEST_URI
     $real_dir,         # actual (real) filesystem directory to display
     @dirlist,          # entire set of files/directories in the directory to display
     $diritem,          # just one of the files/directories in the directory to display
     $filedir,          # actual file *OR* directory name - no path info
     $path,             # the path info for $filedir
     @filepart,         # parts of $filedir (basename, extension)
     $icon,             # type of icon to display (depends on extension
     $debug);           # 1 for debug, 0 for not


$debug = 0;


print header;



# ############################################################################
#
# Configure all aliased paths here.
#
# The alias (left side) references the real path ($alias => $path)
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
# ############################################################################


%alias_doc_roots = (
  'pub'          => '/nfs/www/public',
  'icons'        => '/var/www/icons'
);



$debug && print "DOCUMENT_ROOT:  " . $ENV{DOCUMENT_ROOT} . "<br>";
$debug && print "REQUEST_URI:  " . $ENV{REQUEST_URI} . "<br>";



#
# parse out the root of the REQUEST_URI to see if it
# matches in %alias_doc_roots
# ----------------------------------------------
#
if ( $ENV{REQUEST_URI} =~ m|/(.+?)/(.*)| ) {
  $uri_root = $1;
}
$debug && print "Root of the REQUEST_URI:  " . $uri_root . "<br>";




#
# check to see if the REQUEST_URI contains an alias
# defined %alias_doc_roots
# ----------------------------------------------
#
if ( $alias_doc_roots{$uri_root} ) {
  $real_dir = $alias_doc_roots{$uri_root}; 
  $debug && print "This is an aliased URI.<br>The filesystem path is:  $real_dir <br>";
  $real_dir =~ s|/$uri_root||;
  $real_dir .= $ENV{REQUEST_URI};
  $debug && print "The filesystem URI is:  $real_dir <br>";
#
#
# or should we just use the standard doc root?
# ----------------------------------------------
#
} else {
  $real_dir = $ENV{DOCUMENT_ROOT} .  $ENV{REQUEST_URI};
}




# Massage the $real_dir variable to transition from URI to filesystem
# (whitespace, quotes, etc.)
# --------------------------------------------------------------------------------
#
$real_dir =~ s/%20/ /g;
$real_dir =~ s/%27/'/g;
$real_dir =~ s/(\s)/\\$1/g;




#
# generate a fully-pathed list of files for the request
# -------------------------------------------------------
#
@dirlist = < $real_dir* >;




#
# Start display of the HTML page
#
# In this case, we've setup a static filename "cgi.header" which
# contains the beginning HTML.
#
# ------------------------------------------------------------------

if (open (FILE, "$ENV{DOCUMENT_ROOT}/cgi.header" )) {
  while (<FILE>) {
    print;
  }
  close FILE;
};




# Massage the REQUEST_URI (whitespace, quotes, etc.) for display purposes
# --------------------------------------------------------------------------------
#
$ENV{REQUEST_URI} =~ s/%20/ /g;
$ENV{REQUEST_URI} =~ s/%27/'/g;
#
print "Directory Listing For: " . $ENV{REQUEST_URI} . "<br><br>";

print "<table>";




# Provide a link to the directory one level up.
#
# Using the Windows XP icons.
# Better would be to detect the OS and use the appropriate set.
#
print "<tr><td><a href='..' class=headingL><img src=/index_icons/winxp/back.png border=0>&nbsp;Parent Directory</a><br><br></td></tr>";



# For each item in the directory...
#
#  - starting first with directories
#
foreach $diritem ( @dirlist ) {

  # handle directories
  #
  if ( -d $diritem ) {

    # split into link (file or directory) and path
    ( $filedir, $path) = fileparse( $diritem );
    $icon = "dir";

    if (! ( $filedir =~ m/thumbnails/ ) ) {

      print "<tr><td>
             <a href=\"$filedir\" 
                class=headingL><img src=/index_icons/winxp/$icon.png border=0>&nbsp;$filedir</a>
             </td></tr>";
    }
  }
}


#
#  - and then moving on to files
#
foreach $diritem ( @dirlist ) {

  # handle files
  #
  if ( ! ( -d $diritem ) ) {
    # split into link (file or directory) and path
    ( $filedir, $path ) = fileparse( $diritem );

    # find the filename extension, if it exists
    @filepart = split( '\.', $diritem );


    # if no filename extension
    if (! $filepart[@filepart-1] ) {
      $icon = "unknown";


    # if extension matches, use appropriate icon
    } else {

        switch (  lc($filepart[@filepart-1])  ) {

          case "bmp"   { $icon = "image"; }
          case "class" { $icon = "java"; }
          case "conf"  { $icon = "text"; }
          case "doc"   { $icon = "doc"; }
          case "gif"   { $icon = "image"; }
          case "gz"    { $icon = "compressed"; }
          case "htm"   { $icon = "web"; }
          case "html"  { $icon = "web"; }
          case "jar"   { $icon = "java"; }
          case "java"  { $icon = "java"; }
          case "jpg"   { $icon = "image"; }
          case "js"    { $icon = "js"; }
          case "key"   { $icon = "key"; }
          case "pdf"   { $icon = "pdf"; }
          case "php"   { $icon = "php"; }
          case "png"   { $icon = "image"; }
          case "ppt"   { $icon = "ppt"; }
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

    # Escape single quotes
    $filedir=~ s/'/\'/;

    # Reset URI to http for creating valid links
    $ENV{REQUEST_URI} =~ s/ /%20/g;
    $ENV{REQUEST_URI} =~ s/'/%27/g;

    # Do not display these files or directories in the directory listing
    # Note: thumbnails is a special directory name that can contain thumbnails of photos
    #       to be displayed alongside the photo filename for easier browsing of the photos
    #
    if (! (   ( $filedir =~ m/TABAFK/ )
           || ( $filedir =~ m/Thumbs.db/ ) 
          )
       )
    {

      #
      # If there is an associated thumbnail
      #
      if ( -e "$path/thumbnails/$filedir" ) {

        print "<tr><td><a href=\"$filedir\" class=headingL><img src=\"$ENV{REQUEST_URI}/thumbnails/$filedir\" border=0></a>&nbsp;<a href=\"$filedir\" class=headingL>$filedir</a></td></tr>";


      #
      # There is NO thumbnail associated with this file
      #
      } else {


        #
        # If the file is one of these types, print a direct link
        #
        if (( $filedir =~ m/(\.a$)/i ) ||
            ( $filedir =~ m/(\.bin$)/i ) ||
            ( $filedir =~ m/(\.bmp$)/i ) ||
            ( $filedir =~ m/(\.class$)/i ) ||
            ( $filedir =~ m/(\.cer$)/i ) ||
            ( $filedir =~ m/(\.doc$)/i ) ||
            ( $filedir =~ m/(\.ear$)/i ) ||
            ( $filedir =~ m/(\.exe$)/i ) ||
            ( $filedir =~ m/(\.gif$)/i ) ||
            ( $filedir =~ m/(\.jar$)/i ) ||
            ( $filedir =~ m/(\.jpg$)/i ) ||
            ( $filedir =~ m/(\.gz$)/i ) ||
            ( $filedir =~ m/(\.o$)/i ) ||
            ( $filedir =~ m/(\.pdf$)/i ) ||
            ( $filedir =~ m/(\.png$)/i ) ||
            ( $filedir =~ m/(\.ps$)/i ) ||
            ( $filedir =~ m/(\.rtf$)/i ) ||
            ( $filedir =~ m/(\.tar$)/i ) ||
            ( $filedir =~ m/(\.tgz$)/i ) ||
            ( $filedir =~ m/(\.vsd$)/i ) ||
            ( $filedir =~ m/(\.war$)/i ) ||
            ( $filedir =~ m/(\.zip$)/i )
           ) {

               print "<tr><td>
                      <a href=\"$filedir\"
                         class=headingL><img src=/index_icons/winxp/$icon.png border=0>&nbsp;$filedir</a>
                      </td></tr>";

        } else {

        #
        # Otherwise, print the link via "index2file.cgi."
        #

          print "<tr><td><a href=\"/cgi-bin/index2file.cgi?$ENV{REQUEST_URI}$filedir\" class=headingL><img src=/index_icons/winxp/$icon.png border=0>&nbsp;$filedir</a></td></tr>";

           
        }
      }
    }
  }
}

#
# Print the link to this script.
#
print "<tr><td><div class=headingL><br><br><i>Directory listings generated by <a href=\"http://www.etpenguin.com/pub/Web_Browser/CGI/CGIndex\" class=headingL>CGIndex</a></i></div></td></tr></table>";



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



# END
# ------------------------------------------------------------------
