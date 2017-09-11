#!/usr/bin/perl -w
#
# showfile.cgi
#
# This file is part of CGIndex.
# https://github.com/userbrett/cgindex
#
# It is called by index.cgi.
# It prints the "text" files and lets the browser handle (display,
# download, etc.) the other files.
#
# ###########################################################################


use strict;
use diagnostics;
use CGI::Carp();
use CGI qw(-compile :all);
use File::Basename;
use Switch;


my ( %alias_doc_roots,  # for any aliased DOCUMENT_ROOT's
     $uri_root,         # the root path of the REQUEST_URI
     $real_dir,         # actual (real) filesystem directory to display
     $filename,         # fully pathed filename
     @urlparts,         # parts of $ENV{REQUEST_URI} 
     $dir_of_file,      # used in split() to link to parent directory
     $name_of_file,     # only the filename - not used except in split()
     $debug);           # 1 for debug, 0 for not - debug prints to the browser


$debug = 0;

print header;


# ############################################################################
#
# Configure the directory aliasing here.
# The alias (left side) references the real path ($alias => $path)
#
# All requests for files come from .../cgi-bin/showfile.cgi, so we set
# /cgi-bin (or whatever your "cgi-bin" directory is) to refer to the
# actual path to the DOCUMENT_ROOT.
#
# For example, if: you have showfile.cgi /var/www/cgi-bin,
# and your files are in /nfs/www/files, then you would configure this as follows:
#
#   %alias_doc_roots = (
#      'cgi-bin'    => '/nfs/www/files'
#   );
#
# ############################################################################


%alias_doc_roots = (
  'pub'          => '/data/webdocs/etpenguin/pub',
  'local_icons'  => '/var/www/local_icons',
  'index_icons'  => '/var/www/index_icons',
  'icons'        => '/var/www/icons'
);

$debug && print "DOCUMENT_ROOT:  " . $ENV{DOCUMENT_ROOT} . "<br>";
$debug && print "REQUEST_URI:  " . $ENV{REQUEST_URI} . "<br>";





#
# There should be one CGI ARG in the REQUEST_URI.
# Parse out the root of the ARG to see if it matches in %alias_doc_roots
# ---------------------------------------------------------------------------------
#
# Split the REQUEST_URI into PATH and ARG
@urlparts = split( '\?', $ENV{REQUEST_URI} );


# Redirect requests witout an ARG
# Meaning, just: http://www.etpenguin.com/cgi-bin/showfile.cgi
if ( @urlparts == 1 ) {
  print redirect('http://www.etpenguin.com');
  exit;
}



#
# Find the root part of the ARG
# ------------------------------------------
#
if ( $urlparts[1] =~ m|/(.+?)/(.*)| ) {
  $uri_root = $1;
}
$debug && print "Directory (root) of the REQUEST_URI:  " . $uri_root . "<br>";



#
# see if the root of the ARG is an alias defined %alias_doc_roots
# -----------------------------------------------------------------
#
if ( $alias_doc_roots{$uri_root} ) {
  $real_dir = $alias_doc_roots{$uri_root}; 
  $debug && print "This is an aliased URI.<br>The filesystem path is:  $real_dir <br>";

  # strip off the end (as its the beginning of the URI)
  $real_dir =~ s|/$uri_root||;
  $debug && print "Stripped the URI portion off:  $real_dir <br>";

  $debug && print "Removing HTML, etc. from the filesystem path...<br>";
  $real_dir =~ s/%20/ /g;
  $real_dir =~ s/%27/'/g;
  $real_dir =~ s/(\s)/\\$1/g;
  $debug && print "Final filesystem root path is:  $real_dir <br>";

  $debug && print "Removing HTML from the REQUEST_URI...<br>";
  $ENV{REQUEST_URI} =~ s/%20/ /g;
  $ENV{REQUEST_URI} =~ s/%27/'/g;

  $debug && print "Appending REQUEST_URI ARG to root path...<br>";
  $filename = $real_dir . $urlparts[1];
  $debug && print "Fully pathed filename is:  $filename<br>";

} else {

  $filename = $ENV{DOCUMENT_ROOT} . $urlparts[1];

}

$filename =~ s/%20/ /g;
$filename =~ s/%27/'/g;



#
# Get the directory of the file so we can present the "Parent Directory" link
#
( $name_of_file, $dir_of_file ) = fileparse( $urlparts[1] );

$debug && print "Name of file is:  $name_of_file<br>";
$debug && print "Path to file is:  $dir_of_file<br>";




#
# Start display of the page
#
# To print plain text files (the orignal work), we print in this order:
#   1. cgi.header
#   2. The text file.
#   3. cgi.footer
#
# For other files (PDF, docx, etc.), the goal is to display them we want to provide
# a direct link to the file so that it can be opened or saved.  To do that,
# there is a check for the file type (by trusting the file extension).
#
# ---------------------------------------------------------------------------


if (open (FILE, "$ENV{DOCUMENT_ROOT}/cgi.header" )) {
  while (<FILE>) {
    print;
  }
  close FILE;
};



#
# Begin a new table
#
print "<table>";



# Provide a link to the directory one level up.
#
# Using the Windows XP icons.
# Better would be to detect the OS and use the appropriate set.
#
print "<tr><td><a href='$dir_of_file' class=headingL><img src=/index_icons/winxp/back.png border=0>&nbsp;Parent Directory</a><br><br></td></tr>";



#
# Print the file
#

if ( ( $filename =~ m/\.gif$/i ) ||
     ( $filename =~ m/\.jpg$/i ) ||
     ( $filename =~ m/\.pdf$/i ) ||
     ( $filename =~ m/\.png$/i ) ) {

  # Handle non-text files first:
  #
  #
  my $dirname = dirname( $filename );
  $dirname =~ s|/data/webdocs/etpenguin||;

  print "<tr><td class=content>";
  print "<font>";
  print "<br>";
  print "Sorry, this code does not display that file inline.";
  print "<br><br>";
  print "&nbsp;&nbsp;&nbsp;&nbsp;<font color=black>$urlparts[1]</font>";
  print "<br><br>";
  print "If you want to try and download the file, please use this link:";
  print "<br><br>";
  print "&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"http://www.etpenguin.com$urlparts[1]\">$urlparts[1]</a>";
  print "<br><br>";
  print "In case the file has been moved or renamed, here is a link to the parent directory of the path that was provided:";
  print "<br><br>";
  print "&nbsp;&nbsp;&nbsp;&nbsp;<a href=\"http://www.etpenguin.com${dirname}\">${dirname}</a>";
  print "<br><br>";
  print "</font>";
  print "</td></tr>";


} else {

  # Display text files inline:
  #
  if (open (FILE, "$filename" )) {
    print "<tr><td><font face=\"courier new\"><pre>";
    while (<FILE>) {
      if (! ( $filename =~ m/.*\.htm/i )) {
        $_ =~ s/</&lt;/g;
        $_ =~ s/>/&gt;/g;
      }
      print;
    }
    print "</pre></tr></td>";
    close FILE;
  } else {
    print "404 - Not found.  Config error I suspect...<br>";
    print "$filename";
  }

}
 

#
# Close down the content and table
#
print "<table><tr><td><div class=headingL><br><br><i><a href=\"http://www.etpenguin.com/pub/Web/CGI/CGIndex\" class=headingL>Files presented (or not) by CGIndex</a></i></div></td></tr></table>";




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
#
# Brett Lee
#



