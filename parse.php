<?php
/**
 * file: parse.php
 * author: xsedla1h@stud.fit.vutbr.cz
 */

include 'regex.php';

define("SUCCESS", 0);
define("OK", 0);
define("ERROR", 1);
define("HEADER_ERROR", 21);
define("OPCODE_ERROR", 22);
define("OTHER_SYNTAX_LEX_ERROR", 23);

/* check_symb() function return codes */
define("R_FALSE", 0); define("R_VAR", 1); define("R_BOOL", 2); define("R_INT", 3);
define("R_STR", 4); define("R_NIL", 5);

/* _____ main _____ */

if (check_args($argv) == ERROR) exit(HEADER_ERROR);

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

$parser->end();

exit(SUCCESS);
/* _____ end of main _____ */


class Parser {
    private $lines;
    private $header_ok;
    private $body_ok;
    private $line_number;
    private $instr_no; /* the number of the currently processed instruction */
    private $xml;

    public function Parser() {
        $this->header_ok = -1; /* -1 initial, 0 OK, 21 header error */
        $this->body_ok = -1; /* same as header, but 22 wrong opcode, 23 other error */
        $this->line_number = 1; /* line counter */
        $this->instr_no = 1; /* line counter */

        while ($line = fgets(STDIN)) { /* Read the input */
            $this->lines[] = $line;
        }

        $this->xml = new XMLer();
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
            $line = str_replace("\n", "", $line);
            $line = preg_split("/[ \t]/", $line);

            /* Now check whether the instruction format is correct */
            $opcode = $line[0];

            /* We can generate the instruction element beforehand... */
            $this->xml->start_el('instruction');
            $this->xml->att('order', (string)$this->instr_no);
            $this->xml->att('opcode', strtoupper($opcode));

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], False);
                $this->xml->arg("arg2", $line[2], False);

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], False);

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], False);

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], True);

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], False);
                $this->xml->arg("arg2", $line[2], False);
                $this->xml->arg("arg3", $line[3], False);

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], False);
                $this->xml->arg("arg2", $line[2], False);

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

                /* Write out xml.. */
                $this->xml->arg("arg1", $line[1], True);
                $this->xml->arg("arg2", $line[2], False);
                $this->xml->arg("arg3", $line[3], False);


            } else {
                fprintf(STDERR, "error: unknown instruction on line %d\n",
                    $this->line_number);
                $this->body_ok = OPCODE_ERROR;
                return ERROR;
            }

            $this->xml->end_el(); /* End the instruction element */
            $this->instr_no++;
        }

        return SUCCESS;
    } 

    /* Functions used to check the correct format of a variable/symbol/label/type */
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
        if (preg_match($op_bool, $str)) {
            return R_BOOL;
        } else if (preg_match($op_str, $str)) {
            return R_STR;
        } else if (preg_match($op_nil, $str)) {
            return R_NIL;
        } else if (preg_match($op_int, $str)) {
            return R_INT;
        } else if (preg_match($op_var, $str)) {
            return R_VAR;
        } else { 
            fprintf(STDERR, "error: incorrect symbol format on line %d\n",
                $this->line_number);
            return R_FALSE;
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

    public function end() {
        $this->xml->end_xml();
    }
}

class XMLer {
    private $xw;

    public function XMLer() {
        $this->xw = new XMLWriter();
        $this->xw->openMemory();
        $this->xw->setIndent(1);
        $this->xw->setIndentString('  ');
        $this->xw->startDocument('1.0', 'UTF-8');
        $this->xw->startElement('program');
    }

    public function start_el($name) {
        $this->xw->startElement($name);
    }

    public function end_el() {
        $this->xw->endElement();
    }

    public function att($name, $value) {
        $this->xw->writeAttribute($name, $value);
    }

    public function text($text) {
        $this->xw->text($text);
    }

    public function arg($name, $value, $is_label) {
        include 'regex.php';
        $this->start_el($name);

        if (preg_match($op_var, $value)) {
            $this->att("type", "var");
            $this->text($this->normalize_xml($value));

        } else if (preg_match($op_int, $value)) {
            $this->att("type", "int");
            $this->text(substr($value, 4));

        } else if (preg_match($op_str, $value)) {
            $this->att("type", "str");
            $this->text($this->normalize_xml(substr($value, 7)));

        } else if (preg_match($op_nil, $value)) {
            $this->att("type", "nil");
            $this->text(substr($value, 4));

        } else {

            if ($is_label and preg_match($op_label, $value)) {
                $this->att("type", "label");
                $this->text($this->normalize_xml($value));

            } else if (!$is_label and preg_match($op_bool, $value)) {
                $this->att("type", "bool");
                $this->text(strtolower(substr($value, 5)));

            } else if (!$is_label and preg_match($op_type, $value)) {
                $this->att("type", "type");
                $this->text(strtolower(($value)));

            } else {
                /* Super unlikely to happen - actually this cannot happen,
                * but who knows.... */
                fprintf(STDERR, "ERROR WRITING SYMBOL TO XML, THIS SHOULD NOT HAPPEN\n");
                exit(42);
            }
        }

        $this->end_el();
    }

    public function end_xml() {
        $this->xw->endElement();
        $this->xw->endDocument();
        echo $this->xw->outputMemory();
    }

    private function normalize_xml($text) {
        return str_replace("'", "&apos;", $text);
    }

}

function check_args($argv) {
    if (count($argv) > 1) {
        if (count($argv) == 2) {
            if ($argv[1] == "--help") {

                fprintf(STDOUT, "Skript typu filtr (parse.php v jazyce PHP 7.4) nacte ze standardniho vstupu zdrojovy kod v\nIPPcode20, zkontroluje lexikalni a syntaktickou spravnost kodu a vypise na standardni\nvystup XML reprezentaci programu.\n");
                exit(SUCCESS);

            } else {
                fprintf(STDERR, "Error: unknown argument %s passed to the script\n",
                    $argv[1]);
                exit(10);
            }

        } else {
            fprintf(STDERR, "Error: illegal argument combination passed to the script\n");
            exit(10);
        }
    }

    return SUCCESS;
}

?>
