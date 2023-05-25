import click

from tidy_tweet.tweet_mapping import create_table_statements
from typing import NamedTuple, List, Tuple, TextIO


class Column(NamedTuple):
    name: str
    type: str
    constraints: str = ""
    comment: str = ""


class ForeignKey(NamedTuple):
    table: str
    column: str
    ref_table: str
    ref_column: str


def parse_table(statement: str) -> Tuple[str, List[Column], str]:
    """
    Parses the create table statements in tidy_tweet.tweet mapping to extract
    the database schema. This parser relies very much on the conventions used
    in the tweet_mapping.py file to write the create table statements - if the
    conventions are changed, this parser will need to be changed.

    An alternative approach would be to create a sample database and then use
    PRAGMA statements to pull out the schema, however this would not retrieve
    the comments in the create table statements which are currently where
    column descriptions are kept.
    """
    lines = [line.strip() for line in statement.splitlines()]

    # Skip any blank lines at the start
    line = lines.pop(0).strip()
    while line == "":
        line = lines.pop(0).strip()

    # first line will be "create table ___ ("
    table_name = line.split()[2]

    table_comment = ""

    columns = []

    for line in lines:
        if line == "" or line == ")" or line == ");":
            continue

        column_def, _, comment = line.partition("--")
        # if there is no "--", the whole line will be in column_def

        column_def = column_def.strip().rstrip(",")
        comment = comment.strip()

        if column_def.startswith("primary key"):
            # This line is actually a table constraint
            column_def, _, conditions = column_def.rpartition(")")
            _, _, key_columns = column_def.partition("(")
            key_columns = key_columns.replace(",", " ").split()
            conditions = "primary key " + conditions.strip()

            if table_comment != "":
                table_comment = table_comment + "; " + conditions
            else:
                table_comment = conditions

            # Add to constraints for appropriate columns
            for i, col in enumerate(columns):
                if col.name in key_columns:
                    del columns[i]
                    columns.insert(
                        i,
                        Column(
                            name=col.name,
                            type=col.type,
                            constraints="primary key " + col.constraints,
                            comment=col.comment,
                        ),
                    )
        elif " " in column_def:
            # This line has at least two words and hence a column definition
            column_def = column_def.split()
            columns.append(
                Column(
                    name=column_def[0],
                    type=column_def[1],
                    constraints=" ".join(column_def[2:]),
                    comment=comment,
                )
            )
        elif len(comment) > 0:
            # This line has a comment that continues from the previous line
            prev_column = columns.pop(len(columns) - 1)
            comment = prev_column.comment + " " + comment
            prev_column = prev_column._replace(comment=comment)
            columns.append(prev_column)

    return table_name, columns, table_comment


def write_table_as_list(
    output: TextIO, table_name: str, columns: List[Column], table_comment: str
):
    """
    Prints a markdown-formatted list of the table columns
    """
    output.write(f"Table **{table_name}**:\n\n")

    for col in columns:
        col_constraints = (" " + col.constraints) if col.constraints else ""
        col_comment = (": " + col.comment) if col.comment else ""

        output.write(f"- **{col.name}** ({col.type}{col_constraints}){col_comment}\n")
    else:
        output.write("\n")

    if len(table_comment) > 0:
        output.write(table_comment + "\n\n")


def write_schema_as_lists(output: TextIO):
    for statement in create_table_statements:
        parsed_name, parsed_columns, table_comment = parse_table(statement)

        write_table_as_list(output, parsed_name, parsed_columns, table_comment)
        output.write("\n")


def write_schema_as_mermaid_er(output: TextIO, with_comments=True):
    """
    Generates a mermaid.js ER diagram of the database schema, formatted within
    a markdown block
    """
    output.write("```mermaid\n")
    output.write("erDiagram\n")

    indent = "    "

    foreign_keys: List[ForeignKey] = []

    # Table definitions
    for statement in create_table_statements:
        table_name, columns, _ = parse_table(statement)

        output.write(indent + f'"{table_name}"' + " {\n")

        for col in columns:
            output.write(indent * 2 + col.type + " " + col.name)

            constraints = col.constraints

            if "primary key" in constraints:
                output.write(" PK")
                constraints = constraints.replace("primary key", "")

                # if this column is both PK & FK there needs to be a comma
                if "references" in constraints:
                    output.write(",")

            if "references" in constraints:
                output.write(" FK")

                # need to identify the whole "references table_name (column_name)"
                ref_start = constraints.find("references")
                ref_end = constraints.find(")", ref_start)

                _, ref_table, ref_col = constraints[ref_start : ref_end + 1].split()
                ref_col = ref_col.strip("()")

                foreign_keys.append(
                    ForeignKey(table_name, col.name, ref_table, ref_col)
                )

                # remove the expression now we've dealt with it
                constraints = constraints[:ref_start] + constraints[ref_end + 1 :]
                # Get rid of any awkward double spaces in the middle
                constraints.replace("  ", " ")

            # Extra constraints go in the comment with any actual comment

            # Mermaid requires double quotes for comments
            if (constraints or col.comment) and with_comments:
                output.write(' "')

                output.write(constraints)

                if constraints and col.comment:
                    output.write(" ")

                # Can't have any double quotes inside the double quotes!
                comment = col.comment.replace('"', "'")
                output.write(comment)

                output.write('"')

            output.write("\n")

        output.write(indent + "}\n")

    # Relationships
    for table, column, ref_table, ref_col in foreign_keys:
        # This is super simple and assumes all relationships are one:many

        description = column.removesuffix("_id").replace("_", " ")

        output.write(indent)
        output.write(table + " |o--o{ " + ref_table + " : " + f'"{description}"')
        output.write("\n")

    output.write("```\n\n")


@click.command()
@click.argument("output_file", type=click.File("w"))
@click.option(
    "--diagram/--skip_diagram",
    default=True,
    help="Include (default) or skip a MermaidJS ER diagram of the schema",
)
@click.option(
    "--table_list/--skip_table_list",
    default=True,
    help="Include (default) or skip a series of text lists of tables and their columns",
)
@click.option(
    "--diagram_comments/--skip_diagram_comments",
    default=False,
    help="Include or skip (default) SQL comments from the MermaidJS diagram (for "
    "readability)",
)
def write_schema_docs(output_file, diagram, table_list, diagram_comments):
    output_file.write("# tidy_tweet database schema\n\n")

    output_file.write(
        "This is an automatically generated document describing the tables and columns "
        "in the tidy_tweet database.\n\n"
    )

    if diagram:
        write_schema_as_mermaid_er(output_file, with_comments=diagram_comments)

    if table_list:
        write_schema_as_lists(output_file)


if __name__ == "__main__":
    write_schema_docs()
