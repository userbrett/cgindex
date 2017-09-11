#!/usr/bin/env perl
#
# createthumbs.pl 
#
# This script will create thumbnails of the photos in a directory,
# recursively.
#
# It requires one argument ( a FULLY PATHED directory - start from / ).

require 5.002;

use strict;
use warnings;
use diagnostics;
use File::Find;
use File::Basename;
use subs qw(syntax walkdir);

my $directory;
my $tsize = 100;
my $tpath = "thumbnails";
my ( $filename, $dirpath );
my $convert = "/usr/bin/convert";

$convert = "$convert -thumbnail ${tsize}x${tsize}+0+0";



# -------------------------------------
# Subroutines
# -------------------------------------

sub syntax {
  print "\n";
  print "Usage: $0 <directory>\n";
  print "\n";
  print "Script to create thumbnails for all JPG's found in the directory.\n";
  print "Thumbnails will be created in a 'thumbnail' directory.\n";
  print "\n";
}

sub walkdir {

  my $directory = shift;


  # Walk the directory... 
  # ----------------------------
  find sub {


    # is this a directory ?
    # ------------------------
    if ( -d $File::Find::name ) {
      print "DIRECTORY: " . $File::Find::name  . "\n";


    # not a directory
    # ----------------------------------------------
    } else {

      if (  # is this a JPG ?
            # ------------------------------
            ( $File::Find::name =~ m/\.jpg$/i ) &&


            # and not a thumbnail ?
            # ------------------------------
            (! ( $File::Find::name =~ m/thumbnails/ ) )

      ) {

            # we need a thumbnail for this file
            # ------------------------------------
            print "Making *NEW* thumbnail for : " . $File::Find::name  . "\n";


            # is there an existing  thumbnail directory for this file?
            # -----------------------------------------------------------

            ( $filename, $dirpath ) = fileparse( $File::Find::name );

            if (! ( -d "$dirpath$tpath" )) {
    
              print "    DOES NOT HAVE A THUMBNAILS DIR: " . "$dirpath$tpath" . "\n";
    
              # then make a thumbnail directory 
              #-----------------------------------------
              print "    MAKING *NEW* THUMBNAIL DIR: " . "$dirpath$tpath"  . "\n";
              mkdir ( "$dirpath$tpath", 0755 )
                 || warn "ERROR MAKING DIRECTORY: $! : " . "$dirpath$tpath";
            }


            # escape some possible characters (could do on same line, but...)
            # -------------------------------------------------------------------
            $File::Find::name =~ s/([\$])/\\$1/g;
            $File::Find::name =~ s/([%])/\\$1/g;
            $File::Find::name =~ s/([#])/\\$1/g;
            $File::Find::name =~ s/([&])/\\$1/g;
            $File::Find::name =~ s/(['])/\\$1/g;
            $File::Find::name =~ s/([(])/\\$1/g;
            $File::Find::name =~ s/([)])/\\$1/g;
            $File::Find::name =~ s/([ ])/\\$1/g;


            # get the backslash escaped info             
            ( $filename, $dirpath ) = fileparse( $File::Find::name );


            # and make the thumbnail
            # -----------------------------------------
            system "$convert $File::Find::name $dirpath$tpath/$filename";
      }
    }
  }, $directory;
}


# -------
# main()
# -------

if (( $#ARGV+1 ) < 1 ) { syntax(); exit; }

$directory = shift;
walkdir( $directory );
exit;

