<?php

/* regex patterns for lexical and syntax checks */
$empty_line = "/\A[ \t]*$/";
$comment_line = "/\A[ \t]*#.*$/";
$header_line = "/\A[ \t]*\.IPPcode20[ \t]*(#.*)?$/";

$comment_after_inst = "/\A[^\n#]*(#.*)$/";
$comment_general = "/[ \t]*#.*/";

/* operation codes - grouped by instruction parameter types */
$oc_move_not_int2char_strlen_type = "/\A((move)|(not)|(int2char)|(strlen)|(type))$/i";
$oc_frame_ret_break = "/\A((createframe)|(pushframe)|(popframe)|(return)|(break))$/i";
$oc_defvar_pops = "/\A((defvar)|(pops))$/i";
$oc_pushs_write_exit_dprint = "/\A((pushs)|(write)|(exit)|(dprint))$/i";
$oc_call_label_jump = "/\A((call)|(label)|(jump))$/i";
$oc_math_comp_logic_str2int_concat_getsetc = "/\A((add)|(sub)|(mul)|(idiv)|(lt)|(gt)|(eq)|(and)|(or)|(str2int)|(concat)|(getchar)|(setchar))$/i";
$oc_read = "/\A(read)$/i";
$oc_jumpif = "/\A((jumpifeq)|(jumpifneq))$/i";

/* operands */

$op_var = "/\A(((GF)|(LF)|(TF))@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$/";
$op_label = "/\A([a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$/";
$op_const = "/\A((bool@((true)|(false)))|(nil@nil)|(int@-?(0|([1-9][0-9]*)))|(string@([!\"$-[\]-~]|(\\\\[0-9]{3}))*))$/";
$op_type = "/\A((int)|(string)|(bool))$/";
?>
