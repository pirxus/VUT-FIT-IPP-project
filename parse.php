<?php
/**
 * file: parse.php
 * author: xsedla1h@stud.fit.vutbr.cz
 */



/* _____ main _____ */
$parser = new Parser();
$parser->parse();

if ($parser->get_header_status() != 0) {

    if ($parser->get_header_status() == -1) {
        fwrite(STDERR, "Warning: empty imput file\n");
    }

    exit(21);
}

if ($parser->get_body_status() > 0) /* Considering an empty program body as legitimate */
    exit($parser->get_body_status());

exit(0);
/* _____ end of main _____ */


class Parser {
    private $lines;
    private $header_ok;
    private $body_ok;

    public function Parser() {
        $this->header_ok = -1; /* -1 initial, 0 OK, 21 header error */
        $this->body_ok = -1; /* same as header, but 22 wrong opcode, 23 other error */

        while ($line = fgets(STDIN)) { /* Read the input */
            $this->lines[] = $line;
        }
    }

    public function  get_header_status() {
        return $this->header_ok;
    }

    public function  get_body_status() {
        return $this->body_ok;
    }

    public function parse() {
        $i = 1; /* line counter */
        if ($this->lines == null) return 0;

        foreach ($this->lines as $line) {

            if ($this->header_ok != 0) { /* Check the input file header */

                if ($this->check_header($line, $i) == 1) { /* Check current line */
                    fwrite(STDERR, "error: Incorrect program header format\n");
                    return 1;
                }

            } else { /* The header has already been checked and is all right */

                if ($this->check_body($line, $i) == 1) {
                    fwrite(STDERR, "error: Incorrect program body format\n");
                    return 1;
                }
            }

            $i++;
        }

        return 0;
    }

    private function check_header($line, $line_number) {
        include 'regex.php';

        if (preg_match($empty_line, $line)) {
            return 0;

        } else if (preg_match($comment_line, $line)) {
            return 0;

        } else if (preg_match($header_line, $line)) {
            $this->header_ok = 0;
            return 0;

        } else {
            $this->header_ok = 21;
            fwrite(STDERR, "error on line %d\n", $line_number);
            return 1;
        }
    }

    private function check_body($line, $line_number) {
        include 'regex.php';
        return 0;
    } 
}

function check_args() {
    return 0;
}


?>
