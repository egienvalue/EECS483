#!/usr/bin/python

import sys
import pprint
import copy
import os
import traceback

#---------------------------------------------------------------------------------
#
#	part 0. Global Variables used in the program
#
# In this part, we designed several data structures to store the global variables
# that we used, most important ones are class_map, imp_map and parent_map, which are
# required to output in PA4. There are build-in classes and methods that are not in 
# ast, so we simply add them during initialization process
#
#---------------------------------------------------------------------------------

ast_lines = []
class_list = []
ast = []
type_filename =  (sys.argv[1])[:-4] + "-type"
fout = open(type_filename, 'w')
class_map = {"Object":[], "Int":[], "String":[], "Bool":[], "IO":[]}
imp_map = \
{
 "Object":[("Object","abort"),("Object","copy"),("Object","type_name")],\
   "Int" :[("Object","abort"),("Object","copy"),("Object","type_name")],\
"String" :[("Object","abort"),("Object","copy"),("Object","type_name"), \
           ("String","concat"),("String","length"),("String", "substr")],\
   "Bool":[("Object","abort"),("Object","copy"),("Object","type_name")],\
     "IO":[("Object","abort"),("Object","copy"),("Object","type_name"),\
           ("IO","in_int"),("IO","in_string"),("IO","out_int"),\
           ("IO","out_string")]
}
parent_map = {"Int":"Object", "String":"Object", "Bool":"Object"}

#---------------------------------------------------------------------------------
#
#	part 1. Class Definition
# In this part, we designed multiple classes for storing ast nodes as did in video 
# guides. This helps us to find any node we want from the root of ast
#
#---------------------------------------------------------------------------------


class Expression(object):
    line_num = None
    exp_type = "No_TYPE"

    def s(self):
        ret = str(self.line_num) + "\n"
        ret += str(self.exp_type) + "\n"
        return ret

    def __init__(self, _line_num):
        self.line_num = _line_num

    def __repr__(self):
        return str(self)

class Integer(Expression):
    int_val = None

    def __init__(self, _line_num, _int_val):
        Expression.__init__(self, _line_num)
        self.int_val = _int_val
        self.exp_type = "Int"

    def __str__(self):
        ret = self.s()
        ret += "integer\n" 
        ret += str(self.int_val)+ "\n"
        return ret
    def __repr__(self):
        ret = self.s()
        ret += "integer\n" 
        ret += str(self.int_val)+ "\n"
        return ret

class String(Expression):
    str_val = None

    def __init__(self, _line_num, _str_val):
        Expression.__init__(self, _line_num)
        self.str_val = _str_val
        self.exp_type = "String"

    def __str__(self):
        ret = self.s()
        ret += "string\n" 
        ret += str(self.str_val) + "\n"
        return ret
    def __repr__(self):
        ret = self.s()
        ret += "string\n" 
        ret += str(self.str_val) + "\n"
        return ret


class TrueExp(Expression):
    def __init__(self, _line_num):
        Expression.__init__(self, _line_num)
        self.exp_type = "Bool"

    def __str__(self):
        ret = self.s()
        ret += "true\n"
        return ret

class FalseExp(Expression):
    def __init__(self, _line_num):
        Expression.__init__(self, _line_num)
        self.exp_type = "Bool"

    def __str__(self):
        ret = self.s()
        ret += "false\n"
        return ret

class IdentifierExp(Expression):
    ident = None
    def __init__(self, _line_num, _ident):
        Expression.__init__(self,_line_num)
        self.ident = _ident

    def __str__(self):
        ret = self.s()
        ret += "identifier\n" 
        ret += str(self.ident)
        return ret

class New(Expression):
    ident = None

    def __init__(self, _line_num, _ident):
        Expression.__init__(self, _line_num)
        self.ident = _ident
        self.exp_type = _ident.ident

    def __str__(self):
        ret = self.s()
        ret += "new\n"
        ret += str(self.ident)
        return ret

class Assign(Expression):
    ident = None
    exp = None

    def __init__(self, _line_num, _ident, _exp):
        Expression.__init__(self, _line_num)
        self.ident = _ident
        self.exp = _exp

    def __str__(self):
        ret = self.s()
        ret += "assign\n"
        ret += str(self.ident)
        ret += str(self.exp)

        return ret

# edit by Jun
class Let(Expression):
    binding_list = []
    exp = None

    def __init__(self, _line_num, _binding_list, _exp):
        Expression.__init__(self, _line_num)
        self.binding_list = _binding_list
        self.exp = _exp

    def __str__(self):
        ret = self.s()
        ret += "let\n"
        ret += str(len(self.binding_list)) + "\n"
        for binding in self.binding_list :
            ret += str(binding)
        ret += str(self.exp)
        return ret

# edit by Jun
class Binding(Expression):
    var_ident = None
    type_ident = None
    initialization = None
    value_exp = None

    def __init__(self, _var_ident, _type_ident, _initialization, _value_exp):
        self.var_ident = _var_ident
        self.type_ident = _type_ident
        self.initialization = _initialization
        self.value_exp = _value_exp
    
    def __str__(self):
        if self.initialization:
            ret = "let_binding_init\n"
        else :
            ret = "let_binding_no_init\n"
        ret += str(self.var_ident)
        ret += str(self.type_ident)
        if self.initialization:
            ret += str(self.value_exp)
        return ret

# edit by Jun
class Case(Expression):
    exp = None
    element_list = []
    
    def __init__(self, _line_num, _exp, _element_list):
        Expression.__init__(self, _line_num)
        self.exp = _exp
        self.element_list = _element_list

    def __str__(self):
        ret = self.s()
        ret += "case\n"
        ret += str(self.exp)
        ret += str(len(self.element_list)) + "\n"
        for element in self.element_list:
            ret += str(element)
        return ret

# edit by Jun
class Case_element(Expression):
    var_ident = None
    type_ident = None
    body_exp = None

    def __init__(self, _var_ident, _type_ident, _body_exp):
        self.var_ident = _var_ident
        self.type_ident = _type_ident
        self.body_exp = _body_exp
    
    def __str__(self):
        ret = str(self.var_ident)
        ret += str(self.type_ident)
        ret += str(self.body_exp)
        return ret

class Dynamic_Dispatch(Expression):
    exp = None
    method_ident = None
    args = None

    def __init__(self, _line_num, _exp, _method_ident, _args):
        Expression.__init__(self, _line_num)

        self.exp = _exp
        self.method_ident = _method_ident
        self.args = _args

    def __str__(self):
        ret = self.s()
        ret += "dynamic_dispatch\n"
        ret += str(self.exp)
        ret += str(self.method_ident)
        ret += str(len(self.args)) + "\n"
    	for arg in self.args:
	        ret += str(arg)
        return ret

class Static_Dispatch(Expression):
    exp = None
    type_ident = None
    method_ident = None
    args = None

    def __init__(self, _line_num, _exp, _type_ident, _method_ident, _args):
        Expression.__init__(self, _line_num)
        self.exp = _exp
        self.type_ident = _type_ident
        self.method_ident = _method_ident
        self.args = _args

    def __str__(self):
        ret = self.s()
        ret += "static_dispatch\n"
        ret += str(self.exp)
        ret += str(self.type_ident)
        ret += str(self.method_ident)
        ret += str(len(self.args)) + "\n"
        for arg in self.args:
            ret += str(arg)

        return ret

class Self_Dispatch(Expression):
    method_ident = None
    args = None

    def __init__(self, _line_num, _method_ident, _args):
        Expression.__init__(self, _line_num)
        self.method_ident = _method_ident
        self.args = _args

    def __str__(self):
        ret = self.s()
        ret += "self_dispatch\n"
        ret += str(self.method_ident)
        ret += str(len(self.args)) + "\n"
        for arg in self.args:
            ret += str(arg)
        return ret

class If(Expression):
    predicate = None
    then_body = None
    else_body = None

    def __init__ (self, _line_num, _predicate, _then_body, _else_body):
        Expression.__init__(self, _line_num)
        self.predicate = _predicate
        self.then_body = _then_body
        self.else_body = _else_body

    def __str__(self):
        ret = self.s()
        ret += "if\n"
        ret += str(self.predicate)
        ret += str(self.then_body)
        ret += str(self.else_body)

        return ret

class While(Expression):
    predicate = None
    body = None

    def __init__(self, _line_num, _predicate, _body):
        Expression.__init__(self, _line_num)
        self.predicate = _predicate
        self.body = _body

    def __str__(self):
        ret = self.s()
        ret += "while\n"
        ret += str(self.predicate)
        ret += str(self.body)

        return ret

class Block(Expression):
    exp_list = None
    def __init__(self, _line_num, _exp_list):
        Expression.__init__(self, _line_num)
        self.exp_list = _exp_list

    def __str__(self):
        ret = self.s()
        ret += "block\n"
        ret += str(len(self.exp_list)) + "\n"
        for exp in self.exp_list:
            ret += str(exp)

        return ret

class Isvoid(Expression):
    exp = None
    def __init__(self, _line_num, _exp):
        Expression.__init__(self, _line_num)
        self.exp = _exp

    def __str__(self):
        ret = self.s()
        ret += "isvoid\n"
        ret += str(self.exp)

        return ret

class Plus(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "plus\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Minus(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "minus\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Times(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "times\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Divide(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "divide\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Lt(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "lt\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Le(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "le\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Eq(Expression):
    lhs = None
    rhs = None

    def __init__(self, _line_num, _lhs, _rhs):
        Expression.__init__(self, _line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += "eq\n"
        ret += str(self.lhs)
        ret += str(self.rhs)

        return ret

class Not(Expression):
    exp = None

    def __init__(self, _line_num, _exp):
        Expression.__init__(self, _line_num)
        self.exp = _exp

    def __str__(self):
        ret = self.s()
        ret += "not\n"
        ret += str(self.exp)

        return ret

class Negate(Expression):
    exp = None

    def __init__(self, _line_num, _exp):
        Expression.__init__(self, _line_num)
        self.exp = _exp

    def __str__(self):
        ret = self.s()
        ret += "negate\n"
        ret += str(self.exp)

        return ret

class Formal(object):
    formal_name = None
    formal_type = None

    def __init__(self, _formal_name, _formal_type):
        self.formal_name = _formal_name
        self.formal_type = _formal_type

    def __str__(self):
        ret = str(self.formal_name)
        ret += str(self.formal_type)

        return ret

    def __repr__(self):
        return str(self)

class Attribute(object):
    attr_name = None
    attr_type = None
    initialization = None
    exp = None

    def __init__(self, _attr_name, _attr_type, _initialization, _exp):
        self.attr_name = _attr_name
        self.attr_type = _attr_type
        self.initialization = _initialization
        self.exp = _exp

    def __str__(self):
        ret = ""
        if self.initialization:
            ret += "attribute_init\n"
        else:
            ret += "attribute_no_init\n"

        ret += str(self.attr_name)
        ret += str(self.attr_type)

        if self.initialization:
            ret += str(self.exp)

        return ret

class Identifier(object):
    line_num = None
    ident = None
    def __init__(self, _line_num, _ident):
        self.line_num = _line_num
        self.ident = _ident

    def __str__(self):
        ret = str(self.line_num) + "\n" + str(self.ident) + "\n"
        return ret

    def __repr__(self):
        return str(self)

class Method(object):
    method_name = None
    formals = []
    method_type = None
    body_exp = None

    def __init__(self, _method_name, _formals, _method_type, _body_exp):
        self.method_name = _method_name
        self.formals = _formals
        self.method_type = _method_type
        self.body_exp = _body_exp

    def __str__(self):
        ret = "method\n"
        ret += str(self.method_name)
        ret += str(len(self.formals)) + "\n"
        for formal in self.formals:
            ret += str(formal)
        ret += str(self.method_type)
        ret += str(self.body_exp)

        return ret

    def __repr__(self):
        return str(self)

class Class(object):
    name_iden = None
    inherits_iden = None
    methods = []
    attributes = []
    features = []

    def __init__(self, _name_iden, _inherits_iden, _attributes, _methods,_features):
        self.name_iden = _name_iden
        self.inherits_iden = _inherits_iden
        self.attributes = _attributes
        self.methods = _methods
        self.features = _features

    def __str__(self):
        ret = str(self.name_iden)
        if self.inherits_iden != None:
            ret += "inherits\n" + str(self.inherits_iden)
        else:
            ret += "no_inherits\n"
        ret += str(len(self.features)) + "\n"
        for feature in self.features:
            ret += str(feature)

        return ret

    def __repr__(self):
        return str(self)


#---------------------------------------------------------------------------------
#
#	part 2. Print Section
# Start by get_line(), this section is able to recursively print all sections in 
# the ast. This part is nothing special, we also get them directly from video guide
#
#---------------------------------------------------------------------------------

def get_line():
    global ast_lines
    if ast_lines == []:
        return
    return ast_lines.pop(0)

def read_identifier():
    line_no = get_line()
    ident_name = get_line()

    return Identifier(line_no, ident_name)

def read_formal():
    formal_name = read_identifier()
    formal_type = read_identifier()

    return Formal(formal_name, formal_type)

def read_binding():
    binding_kind = get_line()
    if binding_kind == "let_binding_init" :
        binding_var_ident = read_identifier()
        binding_type_ident = read_identifier()
        binding_value_exp = read_exp()
        return Binding(binding_var_ident,binding_type_ident, True, \
                binding_value_exp)
    elif binding_kind == "let_binding_no_init":
        binding_var_ident = read_identifier()
        binding_type_ident = read_identifier() 
        return Binding(binding_var_ident,binding_type_ident,False, None)

def read_case_elem():
    case_elem_var = read_identifier()
    case_elem_type = read_identifier()
    case_elem_body = read_exp()
    return Case_element(case_elem_var,case_elem_type,case_elem_body)

def read_exp():
    line_number = get_line()
    exp_name = get_line()

    if exp_name == 'assign':
        assignee = read_identifier()
        rhs = read_exp()
        return Assign(line_number, assignee, rhs)

# edit by Jun
    elif exp_name == 'let':
        num_bindings = int(get_line())
        binding_list = []
        for i in range(num_bindings):
            binding_list.append(read_binding())
        let_body = read_exp()
        return Let(line_number, binding_list, let_body)
      
# edit by Jun
    elif exp_name == 'case':
        case_exp = read_exp()
        num_case_elem = int(get_line())
        case_elem_list = []
        for i in range(num_case_elem):
           case_elem_list.append(read_case_elem())
        return Case(line_number, case_exp, case_elem_list)


    elif exp_name == 'dynamic_dispatch':
        obj_name = read_exp()
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())

        return Dynamic_Dispatch(line_number, obj_name, method_name, args)

    elif exp_name == 'static_dispatch':
        obj_name = read_exp()
        type_name = read_identifier()
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())

        return Static_Dispatch(line_number, obj_name, type_name, method_name, args)

    elif exp_name == 'self_dispatch':
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())

        return Self_Dispatch(line_number, method_name, args)

    elif exp_name == 'if':
        predicate = read_exp()
        then_body = read_exp()
        else_body = read_exp()

        return  If(line_number, predicate, then_body, else_body)

    elif exp_name == 'while':
        predicate = read_exp()
        body_exp = read_exp()

        return While(line_number,predicate, body_exp)

    elif exp_name == 'block':
        num_exps = int(get_line())
        exps = []
        for i in range(num_exps):
            exps.append(read_exp())

        return Block(line_number, exps)

    elif exp_name == 'new':
        return New(line_number, read_identifier())


    elif exp_name == 'isvoid':
        return Isvoid(line_number, read_exp())

    elif exp_name == 'plus':
        return Plus(line_number, read_exp(), read_exp())

    elif exp_name == 'minus':
        return Minus(line_number, read_exp(), read_exp())

    elif exp_name == 'times':
        return Times(line_number, read_exp(), read_exp())

    elif exp_name == 'divide':
        return Divide(line_number, read_exp(), read_exp())

    elif exp_name == 'lt':
        return Lt(line_number, read_exp(), read_exp())

    elif exp_name == 'le':
        return Le(line_number, read_exp(), read_exp())

    elif exp_name == 'eq':
        return Eq(line_number, read_exp(), read_exp())

    elif exp_name == 'not':
        return Not(line_number, read_exp())

    elif exp_name == 'negate':
        return Negate(line_number, read_exp())

    elif exp_name == 'integer':
        return Integer(line_number, int(get_line()))

    elif exp_name == 'string':
        return String(line_number, get_line())

    elif exp_name == 'identifier':
        return IdentifierExp(line_number, read_identifier())

    elif exp_name == 'true':
        return TrueExp(line_number)

    elif exp_name =='false':
        return FalseExp(line_number)

def read_feature():
    feature_kind = get_line()

    if feature_kind == 'attribute_no_init':
        feature_name = read_identifier()
        feature_type = read_identifier()
        return Attribute(feature_name, feature_type, False, None)

    elif feature_kind == 'attribute_init':
        feature_name = read_identifier()
        feature_type = read_identifier()
        feature_init = read_exp()
        return Attribute(feature_name, feature_type, True, feature_init)

    elif feature_kind == 'method':
        feature_name = read_identifier()
        formal_list = []
        num_formals = int(get_line())
        for i in range(num_formals):
            formal_list.append(read_formal())
        feature_type = read_identifier()
        feature_body = read_exp()

        return Method(feature_name, formal_list, feature_type, feature_body)

def read_class():
    class_info = read_identifier()

    check_inherits = get_line()

    parent = None
    if check_inherits == 'inherits':
        parent = read_identifier()

    num_features = int(get_line())
    attr_list = []
    method_list = []

    feature_list = []

    for i in range(num_features):
        feature_list.append(read_feature())
    for feature in feature_list:
        if isinstance(feature, Attribute):
            attr_list.append(feature)
        elif isinstance(feature,Method):
            method_list.append(feature)
    return Class(class_info, parent, attr_list, method_list, feature_list)

def read_ast():
    num_classes = int(get_line())

    for i in range(num_classes):
        class_list.append(read_class())

    return class_list
  
#---------------------------------------------------------------------------------
#
#	part 3. Type check
# In this section, we wrote a big type check function. This part is the most important
# part in our program. Please see notes for each case for more details. The type check 
# function takes three parameters: current_cls, astnode and symbol_table. current_cls 
# records the current class that we are checking, astnode is the node we are checking,
# symbol_table is some map we have to maintain during the checking process for the 
# scope checking.
#
#---------------------------------------------------------------------------------

def tc(current_cls, astnode, symbol_table = {}):
    global ast
    global modified_ast
    global internal_ast

    # part 3.1 class case: if the node is a class

    if isinstance(astnode, Class):
        # creat new symbol table for class
        symbol_table = {}

        # check redefined Object
        if astnode.name_iden.ident in ["Object","Int","String","Bool","SELF_TYPE", "IO"]:
            raise Exception("ERROR: "+astnode.name_iden.line_num+": Type-Check: class "+astnode.name_iden.ident+" redefined")

        # check main method exist
        if astnode.name_iden.ident == "Main":
            if "main" not in [x[1] for x in imp_map["Main"]] :
                raise Exception("ERROR: 0: Type-Check: Class Main " + \
                                "method main not found")
            cls_name = [x[0] for x in imp_map["Main"] if x[1] == "main"][0]
            method_instance = find_instance(cls_name, "main", ast)
            if method_instance.formals != []:
                raise Exception("ERROR: 0: Type-Check: class Main method main with 0 parameters not found")
                
        # check method redefined
        for i, method in enumerate(astnode.methods):
            for j, target_method in enumerate(astnode.methods):
                if i!=j and method.method_name.ident == \
                            target_method.method_name.ident:
                    raise Exception("ERROR: " + \
                            target_method.method_name.line_num + \
                            ":"+"Type-Check: Class "+ \
                            astnode.name_iden.ident + "redifines method")
        
        # check attribute redefined
        check_list = []
        for attribute in class_map[astnode.name_iden.ident]:
            if attribute.attr_name.ident in check_list:
                raise Exception("ERROR: "+attribute.attr_name.line_num+\
                        ": Type-Check: class "+astnode.name_iden.ident+\
                        " redefines attribute "+attribute.attr_name.ident)
            else :
                check_list.append(attribute.attr_name.ident)
 
        # add every attibute to symbol_table
        for attribute in class_map[astnode.name_iden.ident]:
            if attribute.attr_name.ident in symbol_table.keys():
                symbol_table[attribute.attr_name.ident].append((attribute.attr_name.ident,attribute.attr_type.ident))
            else:
                symbol_table[attribute.attr_name.ident]=[(attribute.attr_name.ident,attribute.attr_type.ident)] 
        
        for attribute in astnode.attributes:
            tc(current_cls,attribute,symbol_table)
        
        for method in astnode.methods:
            tc(current_cls,method,symbol_table)

    # part 3.2 method case: if the astnode is a method
     
    elif isinstance(astnode, Method):
	# check method return type   
        if astnode.method_type.ident not in class_map.keys()+["SELF_TYPE"]:
            raise Exception("ERROR: "+astnode.method_name.line_num+\
                    ": Type-Check: class has method "+\
                    astnode.method_name.ident + \
                    " with unknown return type " + astnode.method_type.ident)

        ## check formals, the formals need to be unique and with known type
        check_list = []
        for formal in astnode.formals:
            if formal.formal_type.ident not in class_map.keys() :
                raise Exception("ERROR: "+formal.formal_type.line_num+\
                        ": Type-Check: class has method "+ \
                        astnode.method_name.ident+ \
                        " with formal parameter of unknown type "+ \
                        formal.formal_type.ident)

            if formal.formal_name.ident == "self":
                raise Exception("ERROR: "+formal.formal_name.line_num+\
                ": Type-Check: class has method "+astnode.method_name.ident+\
                " with formal parameter named self")
            if formal.formal_name.ident in check_list:
                raise Exception("ERROR: "+ formal.formal_name.line_num+\
                        ": Type-Check: class "+formal.formal_name.ident+\
                        " duplicate formal "+formal.formal_name.ident)
            else :
                check_list.append(formal.formal_name.ident)

	# update symbol table using formals
        for formal in astnode.formals:
            if formal.formal_name.ident in symbol_table.keys():
	        symbol_table[formal.formal_name.ident].append \
                        ((formal.formal_name.ident, formal.formal_type.ident))
            else:
	        symbol_table[formal.formal_name.ident] = \
                        [(formal.formal_name.ident, formal.formal_type.ident)]

        # check if the return type the same as the expression type
        method_body_type = tc(current_cls,astnode.body_exp,symbol_table)
        if method_body_type == "SELF_TYPE" and astnode.method_type.ident !=\
        "SELF_TYPE":
            method_body_type = current_cls.name_iden.ident
        if astnode.method_type.ident != \
                find_common_ancestor(method_body_type,astnode.method_type.ident):
            raise Exception("ERROR: "+astnode.method_type.line_num+\
                    ": Type-Check: "+method_body_type+" does not conform to "+\
                    astnode.method_type.ident+" in "+ astnode.method_name.ident)
        
        # pop formals out of the symbol table
        for formal in astnode.formals:
            symbol_table[formal.formal_name.ident].pop()
            if symbol_table[formal.formal_name.ident] == []:
                symbol_table.pop(formal.formal_name.ident)

    # part 3.3 attribut case: if the node is an attribute
    elif isinstance(astnode, Attribute):
	# check if the attribute has unkown type
        if astnode.attr_type.ident not in class_map.keys()+["SELF_TYPE"]:
            raise Exception("ERROR: "+astnode.attr_type.line_num+\
                    ": Type-Check: class "+current_cls.name_iden.ident+\
                    " has attribute "+astnode.attr_name.ident+
                    " with unknown type "+astnode.attr_type.ident)

	# attribute can not be named self
        if astnode.attr_name.ident == "self":
            raise Exception("ERROR: "+astnode.attr_name.line_num + \
            ": Type-Check: class has an attribute named self")

        # check if the attribute is correctly initiated
        if astnode.initialization :
            t1 = tc(current_cls,astnode.exp, symbol_table)
            if t1 == "SELF_TYPE" and astnode.attr_type.ident != "SELF_TYPE":
                t1 = current_cls.name_iden.ident
            if astnode.attr_type.ident != find_common_ancestor(t1,astnode.attr_type.ident):
                raise Exception("ERROR: "+astnode.exp.line_num+\
                        ": Type-Check: "+t1+\
                        " does not conform to "+astnode.attr_type.ident+\
                        " in initialized attribute")

    # part 3.4 expression case: if the astnode is an expr
       
    elif isinstance(astnode, Let):
	# check if binding in let has unknown type
        for binding in astnode.binding_list:
            if binding.type_ident.ident not in class_map.keys()+["SELF_TYPE"]:
                raise Exception("ERROR: "+binding.type_ident.line_num+\
                        ": Type-Check: unknown type "+binding.type_ident.ident)

	    # self can not appear in a lat expr
            if binding.var_ident.ident == "self":
                raise Exception("ERROR: "+binding.var_ident.line_num+\
                        ": Type-Check: binding self in a let is not allowed")
	    
            # undate symbol table
            if binding.var_ident.ident in symbol_table.keys():
                symbol_table[binding.var_ident.ident].append((binding.var_ident.ident,binding.type_ident.ident))
            else:
                symbol_table[binding.var_ident.ident]=[(binding.var_ident.ident,binding.type_ident.ident)] 
	    
            # check if binding type not equal to binding identifier type
            if binding.initialization:
                binding_type = \
                tc(current_cls,binding.value_exp,symbol_table)
                if binding.type_ident.ident != \
                        find_common_ancestor(binding.type_ident.ident,
                                binding_type):
                            raise Exception("ERROR: "+
                                    binding.var_ident.line_num + ": Let")
	
        # update symbol table
	t1 = tc(current_cls, astnode.exp, symbol_table )
        for binding in astnode.binding_list:	
	    symbol_table[binding.var_ident.ident].pop()
            if symbol_table[binding.var_ident.ident] == []:
                symbol_table.pop(binding.var_ident.ident)

	astnode.exp_type = t1
	return t1
    
    elif isinstance(astnode, String):
        astnode.exp_type = "String"
	return "String"

    elif isinstance(astnode, Integer):
        astnode.exp_type = "Int"
	return "Int"
    
    # check if identifier is in symbol table, if not raise exception
    elif isinstance(astnode, Identifier):
        if astnode.ident == "self":
            return "SELF_TYPE"

	if astnode.ident not in symbol_table.keys():
            raise Exception ("ERROR: "+astnode.line_num+\
                    ": Type-Check: unbound identifier "+astnode.ident)
	else:
	    return symbol_table[astnode.ident][-1][1]
    
    # arithmetic check
    elif isinstance(astnode, (Plus, Minus, Times, Divide)):

	t1 = tc(current_cls,astnode.lhs, symbol_table)
	t2 = tc(current_cls,astnode.rhs, symbol_table)
	if (t1 == "Int" and t2 == "Int"):
	    astnode.exp_type = "Int"
	    return "Int"
	else:
	    raise Exception ("ERROR: "+astnode.line_num+\
                    ": Type-Check: arithmetic error")
    
    # comparison check
    elif isinstance(astnode, (Le, Eq, Lt)):

        t1 = tc(current_cls,astnode.lhs, symbol_table)
        t2 = tc(current_cls,astnode.rhs, symbol_table)
        if (t1 in ["Bool","Int","String"] or t2 in ["Bool","Int","String"]) and (t1 != t2):
            raise Exception ("ERROR: "+astnode.line_num+\
                    ": Type-Check: comparison between "+t1+" and "+t2)
        astnode.exp_type = "Bool"
        return "Bool"         

    elif isinstance(astnode, TrueExp):
        astnode.exp_type = "Bool"
        return "Bool" 

    elif isinstance(astnode, FalseExp):
        astnode.exp_type = "Bool"
        return "Bool"   
    
    # assign check 
    elif isinstance(astnode, Assign):

        assign_ident_type = tc(current_cls,astnode.ident, symbol_table)
        assign_exp_type = tc(current_cls,astnode.exp, symbol_table)
	
        # check assign to self
        if astnode.ident.ident == "self":
            raise Exception("ERROR: "+astnode.line_num+": Type-Check: cannot assign to self")
	
        # check is exp conform to identifier
        if assign_ident_type != find_common_ancestor(assign_ident_type,
                assign_exp_type): 
            raise Exception("ERROR: "+astnode.line_num+\
                    ": Type-Check: "+assign_exp_type+" does not conform to "+\
                    assign_ident_type+\
                    " in assignment")
        astnode.exp_type = assign_exp_type
        return astnode.exp_type
    
    # can not new a class without definition first
    elif isinstance(astnode, New):
        if astnode.ident.ident not in class_map.keys()+["Object", "SELF_TYPE"]:
                raise Exception("ERROR: "+astnode.ident.line_num+\
                        ": Type-Check: unknown type "+astnode.ident.ident)
        if astnode.ident.ident == "SELF_TYPE":
            astnode.exp_type = "SELF_TYPE"
        else :
            astnode.exp_type = astnode.ident.ident
        return astnode.exp_type
    
    # if check
    elif isinstance(astnode, If):

        node_topo = []
        predicate_type = tc(current_cls, astnode.predicate, symbol_table)
        then_body_type = tc(current_cls,astnode.then_body, symbol_table)
        else_body_type = tc(current_cls,astnode.else_body, symbol_table)
	
        # predicate type must be bool
        if predicate_type != "Bool":
            raise Exception("ERROR: "+astnode.line_num+\
                    ": Type-Check: conditional has type "+predicate_type+" instead of Bool")
        if then_body_type == "SELF_TYPE" and else_body_type == "SELF_TYPE":
            astnode.exp_type = "SELF_TYPE"
            return astnode.exp_type

        if then_body_type == "SELF_TYPE":
            then_body_type = current_cls.name_iden.ident
        if else_body_type == "SELF_TYPE":
            else_body_type = current_cls.name_iden.ident
        astnode.exp_type = find_common_ancestor(then_body_type, else_body_type)
        return astnode.exp_type


    elif isinstance(astnode, Block):

        for i in range(len(astnode.exp_list)):
            block_exp_type = tc(current_cls,astnode.exp_list[i], symbol_table)
        astnode.exp_type = block_exp_type
        return block_exp_type
    
    # while check
    elif isinstance(astnode, While):

        predicate_type = tc(current_cls,astnode.predicate, symbol_table)
        body_type = tc(current_cls,astnode.body, symbol_table)
	# conditional type must be bool
        if predicate_type != "Bool":
            raise Exception("ERROR: "+astnode.line_num+ \
                    ": Type-Check: conditional has type "+predicate_type+ \
                    "instead of Bool")
        astnode.exp_type = "Object"
        return "Object"
        
    elif isinstance(astnode, Isvoid):

        tc(current_cls,astnode.exp, symbol_table)
        astnode.exp_type = "Bool"
        return "Bool"
    
    elif isinstance(astnode, IdentifierExp):
        t1 = tc(current_cls,astnode.ident, symbol_table)
        astnode.exp_type = t1
        return t1

    elif isinstance(astnode, Not):
	# not exp type must be bool
        exp_type = tc(current_cls,astnode.exp, symbol_table)
        if exp_type != "Bool":
            raise Exception("ERROR: "+astnode.line_num+ \
                    ": Type-Check: Not has type "+exp_type+ \
                    "instead of Bool")
        astnode.exp_type = "Bool"
        return "Bool"
    
    elif isinstance(astnode, Negate):
	# negate exp type must be int
        exp_type = tc(current_cls,astnode.exp, symbol_table)
        if exp_type != "Int":
            raise Exception("ERROR: "+astnode.line_num+ \
                    ": Type-Check: Negate has type "+exp_type+ \
                    "instead of Int")
        astnode.exp_type = "Int"
        return "Int"
    
    # dynamic_dispatch check
    elif isinstance(astnode, Dynamic_Dispatch):
        d_dispatch_exp_type = tc(current_cls,astnode.exp, symbol_table)
        if d_dispatch_exp_type == "SELF_TYPE":
            d_dispatch_exp_type_new = current_cls.name_iden.ident
        else:
            d_dispatch_exp_type_new = d_dispatch_exp_type
        t = []
        for arg in astnode.args:
            temp = tc(current_cls,arg,symbol_table)
            if temp == "SELF_TYPE":
                temp = current_cls.name_iden.ident
            t.append(temp)

        # check existence of method
        if astnode.method_ident.ident not in [x[1] for x in
                imp_map[d_dispatch_exp_type_new]]:
            raise Exception("ERROR: "+astnode.line_num+\
                    ": Type-Check: unknown method "+astnode.method_ident.ident+\
                    " in dispatch on "+\
                    d_dispatch_exp_type)

        method_tuple = [x for x in imp_map[d_dispatch_exp_type_new] if\
                x[1]==astnode.method_ident.ident][0]
        method_instance = \
        find_instance(method_tuple[0],method_tuple[1],ast+internal_ast) 
        t_prime = [formal.formal_type.ident for formal in method_instance.formals]
        if len(t_prime)!= len(t):
            raise Exception("ERROR: "+astnode.line_num)
        for i in range(len(t)):
            if t_prime[i] != find_common_ancestor(t_prime[i],t[i]):
                raise Exception("ERROR: "+astnode.line_num+\
                        ": Type-Check: argument #"+str(i+1)+" type "+t[i]+\
                        " does not conform to formal type "+t_prime[i])
        if isinstance(method_instance.body_exp, str):
            if method_instance.method_type.ident == "SELF_TYPE":
                astnode.exp_type = d_dispatch_exp_type
                return astnode.exp_type
            else:
                astnode.exp_type = method_instance.method_type.ident
                return astnode.exp_type

        else:

            if method_instance.method_type.ident == "SELF_TYPE":
                astnode.exp_type = d_dispatch_exp_type
                return astnode.exp_type
            else:
                astnode.exp_type = method_instance.method_type.ident
                return astnode.exp_type
    
    # static_dispatch check
    elif isinstance(astnode, Static_Dispatch):
        # check the existence of method
        s_dispatch_exp_type = tc(current_cls,astnode.exp, symbol_table)
        if s_dispatch_exp_type == "SELF_TYPE":
            s_dispatch_exp_type_new = current_cls.name_iden.ident
        else:
            s_dispatch_exp_type_new = s_dispatch_exp_type
        t = []
        for arg in astnode.args:
            temp = tc(current_cls,arg,symbol_table)
            if temp == "SELF_TYPE":
                temp = current_cls.name_iden.ident
            t.append(temp)
        
        # check if method is in imp map
        if astnode.method_ident.ident not in [x[1] for x in
                imp_map[s_dispatch_exp_type_new]]:
            raise Exception("ERROR: "+astnode.line_num+\
                    ": Type-Check: unknown method "+astnode.method_ident.ident+\
                    " in dispatch on"+\
                    s_dispatch_exp_type)

        method_tuple = [x for x in imp_map[s_dispatch_exp_type_new] if\
                x[1]==astnode.method_ident.ident][0]
        method_instance = \
        find_instance(method_tuple[0],method_tuple[1],ast+internal_ast) 
        t_prime = [formal.formal_type.ident for formal in \
                 method_instance.formals]
	
        # check if the method has enough number of formals
        if len(t_prime)!= len(t):
            raise Exception("ERROR: "+astnode.line_num) 
        
        # formal check : type must agree 
        for i in range(len(t)):
            if t_prime[i] != find_common_ancestor(t_prime[i],t[i]):
                raise Exception("ERROR: "+astnode.line_num+\
                        ": Type-Check: argument #"+str(i+1)+" type "+t[i]+\
                        " does not conform to formal type "+t_prime[i])
        
        if astnode.type_ident.ident != \
                        find_common_ancestor(astnode.type_ident.ident,
                                s_dispatch_exp_type_new) :
            raise Exception("ERROR: "+astnode.line_num+": Type-Check: "+\
                    s_dispatch_exp_type_new+" does not conform to "+\
                    astnode.type_ident.ident+" in static dispatch") 

        if isinstance(method_instance.body_exp, str):
            if method_instance.method_type.ident == "SELF_TYPE":
                astnode.exp_type = s_dispatch_exp_type
                return astnode.exp_type
            else:
                astnode.exp_type = method_instance.method_type.ident
                return astnode.exp_type

        else:

            if method_instance.method_type.ident == "SELF_TYPE":
                astnode.exp_type = s_dispatch_exp_type
                return astnode.exp_type
            else:
                astnode.exp_type = method_instance.method_type.ident
                return astnode.exp_type
    
    # self_dispatch checl
    elif isinstance(astnode, Self_Dispatch):
        t = []
        for arg in astnode.args:
            temp = tc(current_cls,arg,symbol_table)
            if temp == "SELF_TYPE":
                temp = current_cls.name_iden.ident
            t.append(temp)

        if astnode.method_ident.ident not in [x[1] for x in
                imp_map[current_cls.name_iden.ident]]:
	    
            # check if the method is in imp map
            raise Exception("ERROR: "+astnode.line_num+\
                    ": Type-Check: unknown method "+astnode.method_ident.ident)

        method_tuple = [x for x in\
                imp_map[current_cls.name_iden.ident] if\
                x[1]==astnode.method_ident.ident][0]
        method_instance = \
        find_instance(method_tuple[0],method_tuple[1],ast+internal_ast) 

        t_prime = [formal.formal_type.ident for formal in \
                 method_instance.formals]
	
        # formal check
        if len(t_prime)!= len(t):
            raise Exception("ERROR: "+astnode.line_num)
        for i in range(len(t)):
            if t_prime[i] != find_common_ancestor(t_prime[i],t[i]):
                raise Exception("ERROR: "+astnode.line_num+\
                        ": Type-Check: argument #"+str(i+1)+" type "+t[i]+\
                        " does not conform to formal type "+t_prime[i])

        astnode.exp_type = method_instance.method_type.ident
        return astnode.exp_type
    
    # case check 
    elif isinstance(astnode, Case):
        t_new = []
        t0 = tc(current_cls,astnode.exp,symbol_table)
        for i,case_element in enumerate(astnode.element_list):
            if case_element.type_ident.ident == "SELF_TYPE":
		
                # check if the branch is self_type
                raise Exception("ERROR: "+case_element.type_ident.line_num+\
                ": Type-Check: using SELF_TYPE as a case branch type is not allowed")
            for j, target_case_element in enumerate(astnode.element_list):
                if j!=i and target_case_element.type_ident.ident == \
                case_element.type_ident.ident:
		
                # check if all the branches return different type
                    raise Exception("ERROR: "+\
                            target_case_element.type_ident.line_num+\
                            ": Type-Check: case branch type "+ \
                            target_case_element.type_ident.ident+\
                            " is bound twice")
	
        # update symbol table
        for case_element in astnode.element_list:
            if case_element.var_ident.ident in symbol_table.keys():
                symbol_table[case_element.var_ident.ident].append((case_element.var_ident.ident,case_element.type_ident.ident))
            else:
                symbol_table[case_element.var_ident.ident]=[(case_element.var_ident.ident,case_element.type_ident.ident)]
            case_element_body_type = tc(current_cls,case_element.body_exp,symbol_table)
            t_new.append(case_element_body_type)
            symbol_table[case_element.var_ident.ident].pop()
            if symbol_table[case_element.var_ident.ident] == []:
                symbol_table.pop(case_element.var_ident.ident)

        while(len(t_new)>1):
            temp = find_common_ancestor(t_new.pop(),t_new.pop())
            t_new.append(temp)
        
        astnode.exp_type = t_new[0]
        return astnode.exp_type
    
    # catch unkown expression, and raise error        
    else:
    	raise Exception ("ERROR: Unkown Expression type!")

#---------------------------------------------------------------------------------
#
#	part 4. Produce Map. 
# This part of our code generates three maps which are stated in part 0.
# These produce-functions are called in the main function below. Note that those 
# three functions are not produced together, each of them are called for some semantic
# check, which will be discussed in more detail in main function.
# Meanwhile, we also defined three print-functions, to print maps as instructed.
# What is more, we defined some helper functions:
#	find_common_ancestor: use to find the common ancestor of two classes, takes 
#				two classes as input, and output their LUB
#	produce_internal_ast: used to produce ast for five build-in classes:
#				Object, IO, Int, String, Bool, return a list of classes
#	find_instance: In our maps, we store the name(String) of classes, however, 
#				when we are perform type checking, we want the instance
#				of the class, this is when this function is called.
#
#---------------------------------------------------------------------------------

def produce_class_map(cls,ast):
    global class_map
    class_list = [c for c in ast]
    if cls.inherits_iden == None:
        class_map[cls.name_iden.ident]=cls.attributes
        return list(class_map[cls.name_iden.ident])
    elif cls.inherits_iden != None:
        parent_cls = filter(lambda x : x.name_iden.ident == cls.inherits_iden.ident,
                        class_list)[0]
        # recursive call
        produce_class_map(parent_cls, ast)
        class_map[cls.name_iden.ident] = \
        class_map[parent_map[cls.name_iden.ident]] + \
                                        cls.attributes
        return list(class_map[cls.name_iden.ident])

def produce_imp_map(cls, ast):
    global imp_map
    class_list = [c for c in ast]
    if cls.inherits_iden == None:
        imp_map[cls.name_iden.ident] = []
        for method in cls.methods :
            imp_map[cls.name_iden.ident].append((cls.name_iden.ident, \
                    method.method_name.ident))
        return list(imp_map[cls.name_iden.ident])
    elif cls.inherits_iden != None:
        parent_cls = filter(lambda x : x.name_iden.ident == cls.inherits_iden.ident,
                        class_list)[0]
        imp_map[cls.name_iden.ident] = produce_imp_map(parent_cls, ast)
        parent_method_name_list = [method_tuple[1] for i,method_tuple in \
                enumerate(imp_map[parent_cls.name_iden.ident])]

        for method in cls.methods:
            if method.method_name.ident in parent_method_name_list :
                i = parent_method_name_list.index(method.method_name.ident)
                parent_method_tuple = imp_map[cls.name_iden.ident][i]
                imp_map[cls.name_iden.ident][i]=(cls.name_iden.ident,
                        method.method_name.ident)
                parent_method = \
                find_instance(parent_method_tuple[0],parent_method_tuple[1], ast)
                ## check formals
                if len(parent_method.formals) != len(method.formals):
                    print "ERROR: "+method.method_name.line_num+\
                        ": Type-Check: class "+cls.name_iden.ident+\
                        " redefines method "+method.method_name.ident+\
                        " and changes number of formals"
                    exit()
                if [formal.formal_type.ident for formal in method.formals] != \
                        [formal.formal_type.ident for formal in
                                parent_method.formals]:
                    print "ERROR: "+method.method_name.line_num+\
                        ": Type-Check: class "+cls.name_iden.ident+\
                        " redefines method "+method.method_name.ident+\
                        " and changes type of formals"
                    exit()
                if parent_method.method_type.ident != method.method_type.ident:
                    print "ERROR: "+method.method_name.line_num+\
                        ": Type-Check: class "+cls.name_iden.ident+\
                        " redefines method "+method.method_name.ident+\
                        " and changes return type"
                    exit()

            else:
                imp_map[cls.name_iden.ident].append((cls.name_iden.ident, \
                    method.method_name.ident))
        
        return list(imp_map[cls.name_iden.ident])
        
        for method in cls.methods:
            if method.method_name.ident in parent_method_name_list :
                i = parent_method_name_list.index(method.method_name.ident)
                imp_map[cls.name_iden.ident][i]=(cls.name_iden.ident,
                        method.method_name.ident)
            else:
                imp_map[cls.name_iden.ident].append((cls.name_iden.ident, \
                    method.method_name.ident))
        
        return list(imp_map[cls.name_iden.ident])

def produce_parent_map(ast):
    global parent_map
    class_list = [c for c in ast]
    for cls in class_list:
        if cls.inherits_iden != None:
            parent_map[cls.name_iden.ident] = cls.inherits_iden.ident

def find_common_ancestor(type1,type2):
            global parent_map
            temp = type1
            node_topo = []
            if temp != "SELF_TYPE" :
                while(parent_map.get(temp)!=None):
                    node_topo.append(temp)
                    temp = parent_map[temp]
            else:
                node_topo.append("SELF_TYPE")
                node_topo.append("Object")
       
            temp = type2
            if temp != "SELF_TYPE" :
                while(parent_map.get(temp)!=None):
                    if temp in node_topo:
                        return temp
                    temp = parent_map[temp]
            else:
                if temp in node_topo:
                    return temp
            # if not found
            return "Object"

def produce_internal_ast():
    name_iden = Identifier("0", "Object")
    inherits_iden = None
    method_names = {"abort":"Object","type_name":"String","copy":"SELF_TYPE"}
    methods = [] 
    method = Method(Identifier("0","abort"), [],Identifier("0","Object"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","copy"), [],Identifier("0","SELF_TYPE"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","type_name"), [],Identifier("0","String"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    Object_class = Class(name_iden, inherits_iden, [],methods, methods+[])

    name_iden = Identifier("0", "IO")
    inherits_iden = Identifier("0","Object") 
    methods = []
    method = Method(Identifier("0","in_int"),
            [],Identifier("0","Int"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","in_string"),
            [],Identifier("0","String"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","out_int"),
            [Formal(Identifier("0","x"),Identifier("0","Int"))],Identifier("0","SELF_TYPE"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","out_string"),
            [Formal(Identifier("0","x"),Identifier("0","String"))],Identifier("0","SELF_TYPE"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    IO_class = Class(name_iden, inherits_iden, [],methods, methods+[])
    
    name_iden = Identifier("0", "Int")
    inherits_iden = Identifier("0","Object")
    methods = []
    Int_class = Class(name_iden, inherits_iden, [],methods, methods+[])

    name_iden = Identifier("0", "Bool")
    inherits_iden = Identifier("0","Object")
    methods = []
    Bool_class = Class(name_iden, inherits_iden, [],methods, methods+[])

    name_iden = Identifier("0", "String")
    inherits_iden = Identifier("0","Object")
    methods = []
    method = Method(Identifier("0","concat"),
            [Formal(Identifier("0","s"),Identifier("0","String"))],Identifier("0","String"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","length"),
            [],Identifier("0","Int"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    method = Method(Identifier("0","substr"),
            [Formal(Identifier("0","i"),Identifier("0","Int")), 
             Formal(Identifier("0","l"),Identifier("0","Int"))],Identifier("0","String"),None)
    method.body_exp = "0" +"\n" +\
                          method.method_type.ident +\
                          "\ninternal\n"+name_iden.ident+"." +\
                          method.method_name.ident+"\n"
    methods.append(method)
    String_class = Class(name_iden, inherits_iden, [],methods, methods+[])

    return [Object_class, Bool_class, IO_class, Int_class, String_class]


def print_imp_map(imp_map, ast):
    imp_map = sorted(imp_map.items())
    ret = "implementation_map\n"
    ret += str(len(imp_map)) + "\n"
    for cls,method_list in imp_map: 
        ret += cls + "\n"
        ret += str(len(method_list)) + "\n"
        for method_tuple in method_list :
            ret += method_tuple[1] + "\n"
            method_instance = find_instance(method_tuple[0],method_tuple[1],ast) 
            ret += str(len(method_instance.formals)) + "\n"
            for formal in method_instance.formals :
                ret += formal.formal_name.ident + "\n"
            ret += method_tuple[0] + "\n"
            ret += str(method_instance.body_exp)
    fout.write(ret)
    return ret

def print_class_map(class_map, ast):
    class_map = sorted(class_map.items())
    ret = "class_map\n"
    ret += str(len(class_map)) + "\n"
    for cls, attribute_list in class_map:
        ret += cls + "\n"
        ret += str(len(attribute_list)) + "\n"
        for attribute in attribute_list :
            if attribute.initialization :
                    ret += "initializer\n" + attribute.attr_name.ident + "\n"+\
                            attribute.attr_type.ident + "\n"
                    ret += str(attribute.exp) 
            else:
                    ret += "no_initializer\n" + attribute.attr_name.ident + "\n"\
                            + attribute.attr_type.ident + "\n"
    fout.write(ret)

def print_parent_map(parent_map, ast):
    parent_map = sorted(parent_map.items())
    ret = "parent_map\n"
    ret += str(len(parent_map)) + "\n"
    for child, parent in parent_map:
        ret += child + "\n" + parent+"\n"
    fout.write(ret)

def find_instance(cls_name, method_name, ast):
    cls_instance = [_cls for _cls in ast if _cls.name_iden.ident == \
                    cls_name][0]
    method_instance = [_method for _method in cls_instance.methods if \
                                _method.method_name.ident == method_name][0]
    return method_instance

#---------------------------------------------------------------------------------
#
#	part 5. Main Function
# This is the pipeline of our program: read ast from -cl-ast, produce parent map,
# class-level pre-check, produce imp map and parent map and print them out. The more
# detailed description is discussed below.
#
#---------------------------------------------------------------------------------


def main():
    global ast_lines
    global class_map
    global imp_map
    global parent_map
    global ast  # the actual ast of the code we
    global modified_ast # ast change all class without inherits to inherits Object
    global internal_ast # ast contain all internal classes
    if len(sys.argv) < 2:
        print("Specify .cl-ast input file.")
        exit()

# part 5.1 read ast produced in PA3 by calling read_ast() function

    with open(sys.argv[1]) as f:
        ast_lines = [l[:-1] for l in f.readlines()]
    internal_ast = produce_internal_ast()
    ast = read_ast()

# part 5.2 produce parent map. Note that in this part, we need to first modify our ast since
# those build-in types are not added in PA3. So we built a ast whose root is Object and generated
# parent map from it

    modified_ast = copy.deepcopy(ast)
    for i,cls in enumerate(modified_ast):
        if cls.inherits_iden == None:
            modified_ast[i].inherits_iden = Identifier("0", "Object")
    modified_ast = modified_ast + internal_ast

    produce_parent_map(modified_ast)

# part 5.3 class level pre-check. 

    ### check if class is defined more than once
    for i, cls in enumerate(ast):
        if cls.name_iden.ident in ["Object"]:
            print "ERROR: "+cls.name_iden.line_num+": Type-Check: class Object redefined"
            exit()
        for j, target_cls in enumerate(ast):
            if i!=j and cls.name_iden.ident == target_cls.name_iden.ident:
                print "ERROR: " + target_cls.name_iden.line_num + ":"\
                    "Type-Check: Class defined multiple times:"\
                    + target_cls.name_iden.ident + "\n"
                exit()

    ## check class inherits from bool int string self_type
    for cls in ast:
        if cls.inherits_iden != None:
            if cls.inherits_iden.ident in ["Int","Bool","String", "SELF_TYPE"]:
                        print "ERROR: "+ cls.inherits_iden.line_num + \
                        ": Type-Check: class Main inherits from " + \
                        cls.inherits_iden.ident
                        exit()


    ### check if class inherits from nonexistent class
    class_names = set([c.name_iden.ident for c in ast])
    class_names.add("IO")
    class_names.add("Object")

    for cls in ast:
        if cls.inherits_iden != None :
            if (not cls.inherits_iden.ident in class_names):
                print "ERROR: " + cls.inherits_iden.line_num + " : "\
                    "Type-Check: Class inherits from non-existent class:"\
                    + cls.inherits_iden.ident
                exit()

    ### check the existance of Main class
    if "Main" not in [cls.name_iden.ident for cls in ast]:
        print "ERROR: 0: Type-Check: class Main not found"
        exit()
    
    ### check inherits circle
    def visit(current_cls):
        if current_cls.inherits_iden == None :
            return 0
        if current_cls.name_iden.ident in t_marked:
            print "ERROR: 0: Type-Check: inheritance cycle"
            exit(0)
        t_marked.append(current_cls.name_iden.ident)
        parent_cls = filter(lambda x : x.name_iden.ident == current_cls.inherits_iden.ident,
                        modified_ast)[0]
        visit(parent_cls)

    t_marked = []
    for cls in modified_ast:
        t_marked=[]
        visit(cls)

# part 5.4 all pre-check done! Now it is safe to produce class map and implementation map
# perform type check for each class by calling type check function

    for cls in ast+internal_ast:
        produce_class_map(cls, ast+internal_ast)
    for cls in modified_ast:
        produce_imp_map(cls, modified_ast)
    try:
        for cls in ast:
            tc(cls,cls)
    except Exception as e:
	print e.message
        exit()

# part 5.5 all check done! Print class map, followed by imp map, followed by parent map, 
# followed by aast as required by PA4

    print_class_map(class_map, modified_ast)
    print_imp_map(imp_map, ast+internal_ast)
    print_parent_map(parent_map, modified_ast)
    # print aast
    fout.write(str(len(ast))+"\n")
    for cls in ast:
        fout.write(str(cls))
    
if __name__ == '__main__':
    main()

