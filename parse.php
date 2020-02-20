<?php
/**
 * file: parse.php
 * author: xsedla1h@stud.fit.vutbr.cz
 */


define("SUCCESS", 0);
define("OK", 0);
define("ERROR", 1);
define("HEADER_ERROR", 21);
define("OPCODE_ERROR", 22);
define("OTHER_SYNTAX_LEX_ERROR", 23);

/* _____ main _____ */

if (check_args() == ERROR) exit(HEADER_ERROR);
$parser = new Parser();
$parser->parse();

if ($parser->get_header_status() != OK) {

    if ($parser->get_header_status() == -1) {
        fprintf(STDERR, "Warning: empty imput file\n");
    }

    exit(HEADER_ERROR);
}

if ($parser->get_body_status() > OK) /* Considering an empty program body as legitimate */
    exit($parser->get_body_status());

exit(SUCCESS);
/* _____ end of main _____ */


class Parser {
    private $lines;
    private $header_ok;
    private $body_ok;
    private $line_number;

    public function Parser() {
        $this->header_ok = -1; /* -1 initial, 0 OK, 21 header error */
        $this->body_ok = -1; /* same as header, but 22 wrong opcode, 23 other error */
        $this->line_number = 1; /* line counter */

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
        if ($this->lines == null) return SUCCESS;

        foreach ($this->lines as $line) {

            if ($this->header_ok != OK) { /* Check the input file header */

                if ($this->check_header($line) == ERROR) { /* Check current line */
                    fprintf(STDERR, "error: Incorrect program header format\n");
                    return ERROR;
                }

            } else { /* The header has already been checked and is all right */

                if ($this->check_body($line) == ERROR) {
                    fprintf(STDERR, "error: Incorrect program body format\n");
                    return ERROR;
                }
            }

            $this->line_number++;
        }

        return SUCCESS;
    }

    private function check_header($line) {
        include 'regex.php';

        if (preg_match($empty_line, $line)) {
            return SUCCESS;

        } else if (preg_match($comment_line, $line)) {
            return SUCCESS;

        } else if (preg_match($header_line, $line)) {
            $this->header_ok = OK;
            return SUCCESS;

        } else {
            $this->header_ok = HEADER_ERROR;
            fprintf(STDERR, "error on line %d\n", $this->line_number);
            return ERROR;
        }
    }

    private function check_body($line) {
        include 'regex.php';

        if (preg_match($empty_line, $line)) {
            return SUCCESS;

        } else if (preg_match($comment_line, $line)) {
            return SUCCESS;

        } else { /* Line contains an instruction */

            /* First remove the incidental comment NOTE: add comment counter */
            $line = preg_replace($comment_general, "", $line);

            /* Split the line into an array for easier manipulation */
            $line = preg_split("/[ \t]/X", $line);

            /* Now check whether the instruction format is correct
            * TODO: operand formats*/
            $opcode = $line[0];

            // MOVE NOT INT2CHAR STRLEN TYPE var symb
            if (preg_match($oc_move_not_int2char_strlen_type, $opcode)) {
                if (count($line) != 3) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

                // Check the operand format
                if (!$this->check_var($line[1]) or !$this->check_symb($line[2])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // CREATEFRAME PUSHFRAME POPFRAME RET BREAK
            } else if (preg_match($oc_frame_ret_break, $opcode)) {
                if (count($line) != 1) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // DEFVAR POPS var
            } else if (preg_match($oc_defvar_pops, $opcode)) {
                if (count($line) != 2) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }
                
                // Check the operand format
                if (!$this->check_var($line[1])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // PUSHS WRITE EXIT DPRINT symb
            } else if (preg_match($oc_pushs_write_exit_dprint, $opcode)) {
                if (count($line) != 2) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }
                
                // Check the operand format
                if (!$this->check_symb($line[1])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // CALL LABEL JUMP label
            } else if (preg_match($oc_call_label_jump, $opcode)) {
                if (count($line) != 2) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }
                
                // Check the operand format
                if (!$this->check_label($line[1])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // ADD SUB MUL IDIV LT GT EQ AND OR STRI2INT CONCAT GETCHAR SETCHAR
            // var symb symb
            } else if (preg_match($oc_math_comp_logic_str2int_concat_getsetc, $opcode)) {
                if (count($line) != 4) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

                // Check the operand format
                if (!$this->check_var($line[1]) or !$this->check_symb($line[2])
                    or !$this->check_symb($line[3])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // READ var type
            } else if (preg_match($oc_read, $opcode)) {
                if (count($line) != 3) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

                // Check the operand formats
                if (!$this->check_var($line[1]) or !$this->check_type($line[2])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            // JUMPIFEQ JUMPIFNEQ label symb symb
            } else if (preg_match($oc_jumpif, $opcode)) {
                if (count($line) != 4) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

                // Check the operand format
                if (!$this->check_label($line[1]) or !$this->check_symb($line[2])
                    or !$this->check_symb($line[3])) {
                    $this->body_ok = OTHER_SYNTAX_LEX_ERROR;
                    return ERROR;
                }

            } else {
                fprintf(STDERR, "error: unknown instruction on line %d\n",
                    $this->line_number);
                $this->body_ok = OPCODE_ERROR;
                return ERROR;
            }
        }

        return SUCCESS;
    } 

    /* Functions used to check the correct format of a variable/symbol/label */
    private function check_var($str) {
        include 'regex.php';
        if (preg_match($op_var, $str)) {
            return True;

        } else { 
            fprintf(STDERR, "error: incorrect variable format on line %d\n",
                $this->line_number);
            return False;
        }
    }

    private function check_symb($str) {
        include 'regex.php';
        if (preg_match($op_const, $str) or preg_match($op_var, $str)) {
            return True;

        } else { 
            fprintf(STDERR, "error: incorrect symbol format on line %d\n",
                $this->line_number);
            return False;
        }
    }

    private function check_label($str) {
        include 'regex.php';
        if (preg_match($op_label, $str)) {
            return True;

        } else { 
            fprintf(STDERR, "error: incorrect label format on line %d\n",
                $this->line_number);
            return False;
        }
    }

    private function check_type($str) {
        include 'regex.php';
        if (preg_match($op_type, $str)) {
            return True;

        } else { 
            fprintf(STDERR, "error: incorrect type format on line %d\n",
                $this->line_number);
            return False;
        }
    }
}

class XMLer {
    public $hello;
}

function check_args() {
    return SUCCESS;
}

?>
