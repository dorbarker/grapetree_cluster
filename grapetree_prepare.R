#!/usr/bin/env Rscript

library(dplyr, warn.conflicts = FALSE)
library(glue, warn.conflicts = FALSE)
library(tibble)
library(getopt)
library(magrittr)

arguments <- function() {

    spec <- c(
        'help',      'h', '0', 'logical',   'Print this help and exit',
        'profile',   'p', '1', 'character', 'Table of strain allele profiles',
        'metadata',  'm', '1', 'character', 'Table of strain metadata',
        'delimiter', 'd', '1', 'character', 'Delimiter character [,]',
        'output',    'o', '1', 'character', 'Output directory'
    ) %>%
    matrix(byrow = TRUE, ncol = 5)

    args <- getopt(spec)
    helptext <- getopt(spec, usage = TRUE)

    if (!is.null(args$help)) {
        cat(helptext)
        quit(status = 0)
    }

    if (is.null(args$profile) & is.null(args$metadata)) {
        cat(helptext)
        quit(status = 0)
    }

    if (is.null(args$delimiter)) {
        args$delimiter <- ','
    }

    args
}


fix_data <- function(profile_path, column_name, delimiter) {

    rename_vars <- list()
    rename_vars[column_name] <- 'rowname'

    profiles <-
        profile_path %>%
        read.table(sep = delimiter,
                   header = TRUE,
                   row.names = 1) %>%
        as_tibble %>%
        rownames_to_column %>%
        rename(!!!rename_vars)

   profiles
}


write_data <- function(fixed_data, outdir, name) {

    path <- glue('{outdir}/{basename(name)}')

    write.table(fixed_data,
                file = path,
                sep = '\t',
                row.names = FALSE,
                quote = FALSE)
}


main <- function() {

    args <- arguments()

    if (!is.null(args$profile)) {
        fixed <- fix_data(args$profile, '#Strain', args$delimiter)
        write_data(fixed, args$output, args$profile)
    }

    if (!is.null(args$metadata)) {
        fixed <- fix_data(args$metadata, 'ID', args$delimiter)
        write_data(fixed, args$output, args$metadata)
    }
}

main()
