<?php
/**
 * @file test.php
 * @brief parse.php is a test module for the parser and interpreter of IPPcode20.
 * @author Simon Sedlacek - xsedla1h
 * @note this module currently supports the --parse-only mode only.
 */

define("SUCCESS", 0);
define("OK", 0);
define("ERROR", 1);


/* _____ main _____ */

/* parse the program arguments and set up corresponding flags in the newly created
 * test class object */
$test = parse_args();

/* _____ end of main _____ */

/* This class holds all the necessary information about the testing process,
 * the flags set to direct the process etc.. */
class Test {

    public $directory;
    public $recursive;
    public $parse_only;
    public $int_only;
    public $parser;
    public $interpreter;
    public $jexamxml;

    public function Test() {
        $this->directory = './'
        $this->recursive = False;
        $this->parse_only = False;
        $this->int_only = False;
        $this->parser = '';
        $this->interpreter = '';
        $this->jexamxml = '/pub/courses/ipp/jexamxml/jexamxml.jar'
    }
}

class HTMLgen {
    private $output;

    public function HTMLgen() {
    }
}


/* This function parses the program arguments, creates a Test class object and sets up
 * corresponding flags within it based on the script parameters. */
function parse_args($argv) {
    $test = new Test();
    $opts = array(
        "help",
        "directory:",
        "recursive",
        "parse-script:",
        "int-script:",
        "parse-only",
        "int-only",
        "jexamxml",
    );

    $options = getopt("", $opts);

    if (count($options) > 0) {
        if (array_key_exists("help")) { /* process the --help parameter (it is exclusive) */

            if (count($options) > 1) {
                fprintf(STDERR,"Error: illegal argument combination - help has to be the only argument\n");
                exit(10);
            } else {
                fprintf(STDOUT, "Skript (test.php v jazyce PHP 7.4) bude sloužit pro automatické testování postupné aplikace parse.php a interpret.py. Skript projde zadaný adresář s testy a využije je pro automatické otestování správné funkčnosti obou předchozích programů včetně vygenerování přehledného souhrnu v HTML 5 do standardního výstupu.\n");
                exit(SUCCESS);
            }
        }

        /* Now get on with the rest... */
        if () {
        }
    }

    return $test;
}

?>
