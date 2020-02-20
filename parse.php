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
        fprintf(STDERR, "Warning: empty imput file\n");
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
        if ($this->lines == null) return 0;

        foreach ($this->lines as $line) {

            if ($this->header_ok != 0) { /* Check the input file header */

                if ($this->check_header($line) == 1) { /* Check current line */
                    fprintf(STDERR, "error: Incorrect program header format\n");
                    return 1;
                }

            } else { /* The header has already been checked and is all right */

                if ($this->check_body($line) == 1) {
                    fprintf(STDERR, "error: Incorrect program body format\n");
                    return 1;
                }
            }

            $this->line_number++;
        }

        return 0;
    }

    private function check_header($line) {
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
            fprintf(STDERR, "error on line %d\n", $this->line_number);
            return 1;
        }
    }

    private function check_body($line) {
        include 'regex.php';

        if (preg_match($empty_line, $line)) {
            return 0;

        } else if (preg_match($comment_line, $line)) {
            return 0;

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
                    $this->body_ok = 23;
                    return 1;
                }

                // Check the operand format
                if (!$this->check_var($line[1]) or !$this->check_symb($line[2])) {
                    $this->body_ok = 23;
                    return 1;
                }

            // CREATEFRAME PUSHFRAME POPFRAME RET BREAK
            } else if (preg_match($oc_frame_ret_break, $opcode)) {
                if (count($line) != 1) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }

            // DEFVAR POPS var
            } else if (preg_match($oc_defvar_pops, $opcode)) {
                if (count($line) != 2) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }
                
                // Check the operand format
                if (!$this->check_var($line[1])) {
                    $this->body_ok = 23;
                    return 1;
                }

            // PUSHS WRITE EXIT DPRINT symb
            } else if (preg_match($oc_pushs_write_exit_dprint, $opcode)) {
                if (count($line) != 2) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }
                
                // Check the operand format
                if (!$this->check_symb($line[1])) {
                    $this->body_ok = 23;
                    return 1;
                }

            // CALL LABEL JUMP label
            } else if (preg_match($oc_call_label_jump, $opcode)) {
                if (count($line) != 2) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }
                
                // Check the operand format
                if (!$this->check_label($line[1])) {
                    $this->body_ok = 23;
                    return 1;
                }

            // ADD SUB MUL IDIV LT GT EQ AND OR STRI2INT CONCAT GETCHAR SETCHAR
            // var symb symb
            } else if (preg_match($oc_math_comp_logic_str2int_concat_getsetc, $opcode)) {
                if (count($line) != 4) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }

                // Check the operand format
                if (!$this->check_var($line[1]) or !$this->check_symb($line[2])
                    or !$this->check_symb($line[3])) {
                    $this->body_ok = 23;
                    return 1;
                }

            // READ var type
            } else if (preg_match($oc_read, $opcode)) {
                if (count($line) != 3) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }

                // Check the operand formats
                if (!$this->check_var($line[1]) or !$this->check_type($line[2])) {
                    $this->body_ok = 23;
                    return 1;
                }

            // JUMPIFEQ JUMPIFNEQ label symb symb
            } else if (preg_match($oc_jumpif, $opcode)) {
                if (count($line) != 4) {
                    fprintf(STDERR, "error: incorrect argument count on line %d\n",
                        $this->line_number);
                    $this->body_ok = 23;
                    return 1;
                }

                // Check the operand format
                if (!$this->check_label($line[1]) or !$this->check_symb($line[2])
                    or !$this->check_symb($line[3])) {
                    $this->body_ok = 23;
                    return 1;
                }

            } else {
                fprintf(STDERR, "error: unknown instruction on line %d\n",
                    $this->line_number);
                $this->body_ok = 22;
                return 1;
            }
        }

        return 0;
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

function check_args() {
    return 0;
}
?>
