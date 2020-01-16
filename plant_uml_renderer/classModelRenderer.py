from codeable_models import CException, CMetaclass
from codeable_models.internal.commons import is_cenum, is_cclassifier, set_keyword_args, is_cstereotype, is_cmetaclass
from plant_uml_renderer.modelRenderer import RenderingContext, ModelRenderer

class ClassifierRenderingContext(RenderingContext):
    def __init__(self):
        super().__init__()
        self.visitedAssociations = set()
        self.renderAssociations = True
        self.renderInheritance = True
        self.renderAttributes = True
        self.excludedAssociations = []
        self.renderExtendedRelations = True
        self.excludedExtendedClasses = []

class ClassModelRenderer(ModelRenderer):
    def renderClassifierSpecification(self, context, cl):
        stereotypeString = ""
        if is_cstereotype(cl):
            stereotypeString = self.renderStereotypesString("stereotype")
        if is_cmetaclass(cl):
            stereotypeString = self.renderStereotypesString("metaclass")
        nameLabel = '"' + stereotypeString + self.padAndBreakName(cl.name) + '"'
        context.addLine("class " + nameLabel + " as " + self.getNodeID(context, cl) + self.renderAttributes(context, cl))

    def renderAttributes(self, context, cl):
        if context.renderAttributes == False:
            return ""
        if len(cl.attributes) == 0: 
            return "" 
        attributeString = "{\n"
        for attribute in cl.attributes:
            attributeString += self.renderAttribute(attribute)
        attributeString += "}\n"
        return attributeString
    
    def renderAttribute(self, attribute):
        type = attribute.type
        t = None
        if is_cenum(type) or is_cclassifier(type):
            t = type.name
        elif type == str:
            t = "String"
        elif type == int:
            t = "Integer"
        elif type == float:
            t = "Float"
        elif type == bool:
            t = "Boolean"
        elif type == list:
            t = "List"
        if t == None:
            raise CException(f"unknown type of attribute: '{attribute!s}")
        return attribute.name + ": " + t + "\n"

    def renderAssociations(self, context, cl, classList):
        if context.renderAssociations == False:
            return
        for association in cl.associations:
            if association in context.excludedAssociations:
                continue
            if not association.source == cl:
                # only render associations outgoing from this class
                continue
            if not association in context.visitedAssociations:
                context.visitedAssociations.add(association)
                if association.target in classList:
                    self.renderAssociation(context, association, classList)
        
    def renderAssociation(self, context, association, classList):
        arrow = " --> "
        if association.aggregation:
            arrow = " o-- "
        elif association.composition:
            arrow = " *-- "

        # as we cannot point directly to the association extended in a metamodel, we put a note 
        # on the association saying which stereotypes extend it
        extendedByString = ""
        firstLoopIteration = True
        for stereotype in association.stereotypes:
            if stereotype in classList:
                if firstLoopIteration:
                    extendedByString = extendedByString + " [extended by: \\n"
                    firstLoopIteration = False
                else:
                    extendedByString = extendedByString + ", "
                extendedByString = extendedByString + f"'{stereotype.name!s}'"
        if extendedByString != "":
            extendedByString = extendedByString + "]"


        label = ""
        if association.name != None and len(association.name) != 0:
            label = ": \"" + association.name + extendedByString + "\" "
        elif extendedByString != "":
            label = ": \"" + extendedByString + "\" "
        headLabel = ""
        if (not (association.aggregation or association.composition)):
            headLabel = " \" " + association.source_multiplicity + " \" "
        tailLabel =  " \" " + association.multiplicity + " \" "

        context.addLine(self.getNodeID(context, association.source) + headLabel +
                arrow + tailLabel + self.getNodeID(context, association.target) + label )
        
    def renderExtendedRelations(self, context, stereotype, classList):
        if context.renderExtendedRelations == False:
            return
        for extended in stereotype.extended:
            if is_cmetaclass(extended):
                if extended in context.excludedExtendedClasses:
                    continue
                if extended in classList:
                    context.addLine(self.getNodeID(context, stereotype) + " --> " +
                        self.getNodeID(context, extended) + ': "' + 
                        self.renderStereotypesString("extended") + '"')

    def renderInheritanceRelations(self, context, classList):
        if context.renderInheritance == False:
            return
        for cl in classList:
            for subClass in cl.subclasses:
                if subClass in classList:
                    context.addLine(self.getNodeID(context, cl) + " <|--- " + self.getNodeID(context, subClass))

    def renderClasses(self, context, classList):
        for cl in classList:
            if not is_cclassifier(cl):
                raise CException(f"'{cl!s}' handed to class renderer is not a classifier'")
            self.renderClassifierSpecification(context, cl)
        self.renderInheritanceRelations(context, classList)
        for cl in classList:
            self.renderAssociations(context, cl, classList)
            if is_cstereotype(cl):
                self.renderExtendedRelations(context, cl, classList)

    def renderClassModel(self, classList, **kwargs):
        context = ClassifierRenderingContext()
        set_keyword_args(context,
                         ["renderAssociations", "renderInheritance", "renderAttributes", "excludedAssociations"], **kwargs)
        self.renderStartGraph(context)
        self.renderClasses(context, classList)
        self.renderEndGraph(context)
        return context.result

    def renderClassModelToFile(self, fileNameBase, classList, **kwargs):
        source = self.renderClassModel(classList, **kwargs)
        self.renderToFiles(fileNameBase, source)
    

