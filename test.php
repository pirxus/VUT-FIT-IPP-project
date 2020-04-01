<?php
/**
 * @file test.php
 * @brief parse.php is a test module for the parser and interpreter of IPPcode20.
 * @author Simon Sedlacek - xsedla1h
 */

define("SUCCESS", 0);
define("OK", 0);
define("ERROR", 1);


/* _____ main _____ */

/* parse the program arguments and set up corresponding flags in the newly created
 * test class object */

$test = new Test($argv);
$test->start_test();
$test->end_test();
exit(SUCCESS);

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
    private $html;
    private $dir; // the currently processed directory

    public function Test($argv) {
        /* Initialize the Test object with the
         * flags extracted from the program arguments*/
        $flags = parse_args($argv);

        $this->directory = $flags['directory'];
        $this->recursive = $flags['recursive'];
        $this->parse_only = $flags['parse-only'];
        $this->int_only = $flags['int-only'];
        $this->parser = $flags['parse-script'];
        $this->interpreter = $flags['int-script'];
        $this->jexamxml = $flags['jexamxml'];

        $this->check_resources();

        if ($this->parse_only) $test_mode = "parse-only";
        else if ($this->int_only) $test_mode = "int-only";
        else $test_mode = "both";
        $this->html = new HTMLgen('index.html', $test_mode);
    }

    public function start_test() {
        /* First create a temporary output file */
        $tmp_out = '___tmp___test___out___.out';
        if (!($tmp_file = fopen($tmp_out, 'w'))) {
            fprintf(STDERR, "Error: Could not create a temporary output file\n");
            exit(99);
        }
        fclose($tmp_file);

        $dirs = new SplQueue(); // create a stack for the yet unprocessed directories
        $dirs->push($this->directory);

        /* sequentially scan all the directories in the stack */
        while (!$dirs->isEmpty()) {

            /* get all the files in the current directory */
            $this->dir = $dirs->pop();
            $path = $this->dir . ((substr($this->dir, -1) == '/') ? '' : '/');
            $files = scandir($path);
            foreach ($files as $file) {

                /* if the current file is a directory, skip it or add it to the dirs
                 * stack */
                if (is_dir($path . $file)) {
                    if ($this->recursive and $file != "." and $file != "..")
                        $dirs->push($path . $file);
                    continue;

                } else {

                    if (preg_match("/.*\.src/", $file)) {
                        if (!is_readable($path . $file)) {
                            fprintf(STDERR, "Error: A source file '%s' wasn't readable\n",
                                   $file);
                            continue;
                        }

                        /* check for all the necessary files for the test and create
                         * them if missing */
                        $this->check_test_exists($path, $file, $files);
                        $output = array();
                        $fail = False;

                        /* run the test */
                        if ($this->parse_only) { // parse only
                            exec('php '.$this->parser.' <'.$path.$file.' >'.$tmp_out. ' 2>'.'/dev/null', $output, $rc_actual);
                        } else if ($this->int_only) { // int only
                            exec('python3 '.$this->interpreter.' --source='.$path.$file.' --input='.$path.substr($file, 0, -4).'.in'.' >'.$tmp_out. ' 2>'.'/dev/null', $output, $rc_actual);
                        } else { // both
                            exec('php '.$this->parser.' <'.$path.$file.' >'.$tmp_out. ' 2>'.'/dev/null', $output, $rc_actual);
                            if ($rc_actual != 0) {
                                $fail = True;
                                $rc_expected = 0;
                                $message = 'parsing failed';
                            } else { // FIXME
                                exec('php '.$this->parser.' <'.$path.$file.' | python3 '.$this->interpreter.' --input='.$path.substr($file, 0, -4).'.in'.' >'.$tmp_out. ' 2>'.'/dev/null', $output, $rc_actual);
                                $fail = False;
                            }
                        }

                        /* check the return code */
                        if (!$fail) {
                            $rc_expected = preg_replace('/\s/', '', shell_exec('cat '.$path.substr($file, 0, -4).'.rc'));
                        }

                        if ($rc_expected == $rc_actual) {
                            if ($rc_actual == 0) {

                                /* Check the script output */
                                if ($this->parse_only) { // parse only
                                    exec('java -jar '.$this->jexamxml.' '.$tmp_out.' '.$path.substr($file, 0, -4).'.out', $output, $rc_match);
                                } else { // int only
                                    exec('diff '.$tmp_out.' '.$path.substr($file, 0, -4).'.out', $output, $rc_match);
                                }

                                if ($rc_match == 0) { // outputs match
                                    fprintf(STDERR, "PASSED: %s\n", $path.$file);
                                    $this->html->add_test_row(True, $path.$file, $rc_expected, $rc_actual, "OK");

                                } else { // wrong output
                                    fprintf(STDERR,
                                        "FAILED: %s, output does not match\n",
                                        $path.$file);
                                    $this->html->add_test_row(False, $path.$file, $rc_expected, $rc_actual, "MISMATCH");
                                }

                            } else {
                                fprintf(STDERR,
                                    "PASSED: %s, expected RC: '%d', got '%d'\n",
                                    $path.$file, $rc_expected, $rc_actual);
                                    $this->html->add_test_row(True, $path.$file, $rc_expected, $rc_actual, "-");
                            }

                        } else {
                            /* Return codes do not match */
                            if (!$fail) $message = '-';
                            fprintf(STDERR,
                                "FAILED: %s, expected RC: '%d', got '%d'\n",
                                $path.$file, $rc_expected, $rc_actual);
                                $this->html->add_test_row(False, $path.$file, $rc_expected, $rc_actual, $message);
                        }

                        unset($output);
                        unset($rc_expected);
                        unset($rc_actual);
                        unset($rc_match);
                    }
                }
            }
        }
    }

    private function check_test_exists($path, $src, $dir) {
        $name = substr($src, 0, -4);
        if (!in_array($name . '.in', $dir))
            $this->create_file($path, $name, '.in', '');
        if (!in_array($name . '.out', $dir))
            $this->create_file($path, $name, '.out', '');
        if (!in_array($name . '.rc', $dir))
            $this->create_file($path, $name, '.rc', '0');
    }

    /* This function is used to create a missing componental test file */
    private function create_file($path, $name, $extension, $content) {
        if (!($file = fopen($path . $name . $extension, 'w'))) {
            fprintf(STDERR, "Error: Could not create a missing file\n");
            exit(99);
        }
        fwrite($file, $content);
        fclose($file);
    }

    /* This function checks if the resources specified for the testing are correct
     * and fully availabile. On failure, this function exits the program with the
     * corresponding exit code */
    private function check_resources() {
        /* Check the test directory */
        if (!is_dir($this->directory)) {
            fprintf(STDERR, "Error: Specified test directory is either not a directory or it does not exist at all\n");
            exit(11);
        }

        /* Check the parser script */
        if (!is_file($this->parser)) {
            fprintf(STDERR, "Error: Specified parse script does not exist\n");
            exit(11);

        } else {
            if (is_dir($this->parser)) {
                fprintf(STDERR, "Error: Specified parse script is actually a directory\n");
                exit(11);
            } else if (!is_readable($this->parser)) {
                fprintf(STDERR, "Error: Specified parse script is not readable\n");
                exit(11);
            }
        }

        /* Check the interpreter script */
        if (!is_file($this->interpreter)) {
            fprintf(STDERR, "Error: Specified interpreter script does not exist\n");
            exit(11);

        } else {
            if (is_dir($this->interpreter)) {
                fprintf(STDERR, "Error: Specified interpreter script is actually a directory\n");
                exit(11);

            } else if (!is_readable($this->interpreter)) {
                fprintf(STDERR, "Error: Specified interpreter script is not readable\n");
                exit(11);
            }
        }

        /* Check the jexamxml script */
        if (!is_file($this->jexamxml)) {
            fprintf(STDERR, "%s\n", $this->jexamxml);
            fprintf(STDERR, "Error: Specified jexamxml script does not exist\n");
            exit(11);

        } else {
            if (is_dir($this->jexamxml)) {
                fprintf(STDERR, "Error: Specified jexamxml script is actually a directory\n");
                exit(11);

            } else if (!is_readable($this->jexamxml)) {
                fprintf(STDERR, "Error: Specified jexamxml script is not readable\n");
                exit(11);
            }
        }
    }

    public function end_test() {
        unlink('___tmp___test___out___.out');
        $this->html->end_html();
    }
}

class HTMLgen {
    private $out;
    private $passed;
    private $failed;

    public function HTMLgen($out, $test_mode) {
        $this->out = fopen($out, 'w') or exit(12); /* open the output html file */
        /* set up the wep page */
        fprintf($this->out, '<!DOCTYPE html><html lang="en"><head><h1>IPP20 TEST RESULTS</h1><h2>Test mode: %s</h2></head><style>table, th, td {border: 1px solid black;}</style><body><table class="testResultTable"><tbody><tr><th><strong>Test</strong></th><th><strong>Expected return code</strong></th><th><strong>Actual return code</strong></th><th><strong>Output match</strong></th></tr>', $test_mode) or exit(99);
    }

    public function add_test_row($passed, $test, $rc_expected, $rc_actual, $output_match) {
        if ($passed) {
            $color = "#7FFF00";
            $this->passed++;
        } else {
            $color = "#DC143C";
            $this->failed++;
        }
        fprintf($this->out, '<tr style="background-color:%s"><td>%s</td><td style="text-align:center">%d</td><td style="text-align:center">%d</td><td style="text-align:center">%s</td></tr>',
                $color, $test, $rc_expected, $rc_actual, $output_match) or exit(99);
    }

    public function end_html() {
        fprintf($this->out, '</tbody></table><p>Total tests run: %d</p> <p>PASSED: %d</p><p>FAILED: %d</p></body></html>',
               $this->passed + $this->failed, $this->passed, $this->failed) or exit(99);
        fclose($this->out);
    }
}


/* This function parses the program arguments, creates a Test class object and sets up
 * corresponding flags within it based on the script parameters. */
function parse_args($argv) {
    $opts = array(
        "help", "directory:", "recursive", "parse-script:", "int-script:",
        "parse-only", "int-only", "jexamxml:",
    );

    $flags = array(
        "directory" => './',
        "recursive" => False,
        "parse-script" => './parse.php',
        "int-script" => './interpret.py',
        "parse-only" => False,
        "int-only" => False,
        //"jexamxml" => '/pub/courses/ipp/jexamxml/jexamxml.jar',
        "jexamxml" => '../jexamxml/jexamxml.jar',
    );

    $options = getopt("", $opts);

    if (count($options) > 0) {
        if (array_key_exists("help", $options)) { /* process the --help parameter (it is exclusive) */

            if (count($options) > 1) {
                fprintf(STDERR,"Error: illegal argument combination - help has to be the only argument\n");
                exit(10);
            } else {
                fprintf(STDOUT, "Skript (test.php v jazyce PHP 7.4) bude sloužit pro automatické testování postupné aplikace parse.php a interpret.py. Skript projde zadaný adresář s testy a využije je pro automatické otestování správné funkčnosti obou předchozích programů včetně vygenerování přehledného souhrnu v HTML 5 do standardního výstupu.\n");
                exit(SUCCESS);
            }
        }

        /* Now get on with the rest... */
        if (array_key_exists("directory", $options)) {
            $flags["directory"] = $options["directory"];
        }

        if (array_key_exists("recursive", $options)) {
            $flags["recursive"] = True;
        }

        if (array_key_exists("parse-script", $options)) {
            $flags["parse-script"] = $options["parse-script"];
        }

        if (array_key_exists("int-script", $options)) {
            $flags["int-script"] = $options["int-script"];
        }

        if (array_key_exists("parse-only", $options)) {
            if (array_key_exists("int-only", $options) or
                array_key_exists("int-script", $options)) {
                fprintf(STDERR,"Error: illegal argument combination - parse-only\n");
                exit(10);
            }

            $flags["parse-only"] = True;
        }

        if (array_key_exists("int-only", $options)) {
            if (array_key_exists("parse-only", $options) or
                array_key_exists("parse-script", $options)) {
                fprintf(STDERR,"Error: illegal argument combination - int-only\n");
                exit(10);
            }

            $flags["int-only"] = True;
        }

        if (array_key_exists("jexamxml", $options)) {
            $flags["jexamxml"] = $options["jexamxml"];
        }
    }

    return $flags;
}

?>
