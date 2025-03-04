<?php
/**
 * @file parse.php
 * @brief This file contains most of the regular expressions used in the parse.php module
 * @author Simon Sedlacek - xsedla1h
 */

/* regex patterns for lexical and syntax checks */
$empty_line = "/\A[ \t]*$/";
$comment_line = "/\A[ \t]*#.*$/";
$header_line = "/\A[ \t]*\.IPPcode20[ \t]*(#.*)?$/i";

$comment_after_inst = "/\A[^\n#]*(#.*)$/";
$comment_general = "/[ \t]*#.*/";

/* operation codes - grouped by instruction parameter types */
$oc_move_not_int2char_strlen_type = "/\A((move)|(not)|(int2char)|(strlen)|(type))$/i";
$oc_frame_ret_break = "/\A((createframe)|(pushframe)|(popframe)|(return)|(break))$/i";
$oc_defvar_pops = "/\A((defvar)|(pops))$/i";
$oc_pushs_write_exit_dprint = "/\A((pushs)|(write)|(exit)|(dprint))$/i";
$oc_call_label_jump = "/\A((call)|(label)|(jump))$/i";
$oc_math_comp_logic_stri2int_concat_getsetc = "/\A((add)|(sub)|(mul)|(idiv)|(lt)|(gt)|(eq)|(and)|(or)|(stri2int)|(concat)|(getchar)|(setchar))$/i";
$oc_read = "/\A(read)$/i";
$oc_jumpif = "/\A((jumpifeq)|(jumpifneq))$/i";

/* operands */

$op_var = "/\A(((GF)|(LF)|(TF))@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$/";
$op_label = "/\A([a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$/";
$op_const = "/\A((bool@((true)|(false)))|(nil@nil)|(int@-?([0-9]+))|(string@([^\s\\\\#]|(\\\\[0-9]{3}))*))$/";
$op_bool = "/\Abool@((true)|(false))$/";
$op_nil = "/\Anil@nil$/";
$op_str = "/\Astring@([^\s\\\\#]|(\\\\[0-9]{3}))*$/";
$op_int = "/\Aint@[\-+]?[0-9]+$/";
$op_type = "/\A((int)|(string)|(bool))$/";

?>
