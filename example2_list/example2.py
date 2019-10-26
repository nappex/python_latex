import utils


nested_product_list = ["first item", "second item", "third item", "detektor"]

template = utils.get_template("./example2_template.tex")
print(template)
variable_dict = {"products": nested_product_list}
utils.compile_pdf_from_template(template, variable_dict, "./ex1.pdf")
