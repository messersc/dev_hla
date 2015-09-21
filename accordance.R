options(stringsAsFactors = FALSE)
#setwd("/vol/cs02/scratch/cmessers/projects/BIH/HLA")
setwd("~/hla/dev")
library(stringr)

build_ref_table <- function(){
# To generate the ref table
  ref <- read.csv("/vol/cs02/scratch/cmessers/projects/BIH/HLA/metadata/nar-02838-met-k-2014-File005.csv", header=FALSE)
  ref = head(ref, -2) #remove last 2 lines! Rubbish in there.
  rownames(ref) = make.names(ref[, 1], unique = T)
  colnames(ref) = make.names(ref[2, ], unique = T)
  ref = ref[3:nrow(ref), grep(pattern = ".*reference", ref[2, ])]
  write.table(ref, file = "ref.csv")
}

# load all result files
# samples should be ordered. 
load_results <- function(d = getwd()){
  #build_ref_table()
  ref <<- read.table("ref.csv", header=TRUE, quote="\"")
  bwakit <<- read.table("bwakit", quote="\"", row.names=1)[1:6]
  hlassign <<- read.table("hlassign", quote="\"", row.names=1)
  optitype <<- read.table("optitype", quote="\"", row.names=1)
}

fit_allele_to_precision <- function(str, regex, ncolon){
  if (str == "0") {
    return("nottyped")
  } else if (sum(str_count(str, pattern=":")) >= ncolon) {
   return(gsub(regex, replacement = '\\1', str))
  } else {
    return("nottyped")
  }
}

compare_allele_pairs <- function(x,y){
  s = sum(x %in% y)
  # test for homozygosity
  if (x[1] == x[2]) if (s == 2) s = s - length(setdiff(y,x))
  return(s)
}

build_performance_table <- function(typer = c("optitype", "bwakit", "hlassign"), precision="4d"){
  
  if      (precision == "2d"){ pattern = "(^[ABC]\\*[0-9]{2}).*" ; ncolon = 0}
  else if (precision == "4d"){ pattern = "(^[ABC]\\*[0-9]{2}:[0-9]{2,3}).*" ; ncolon = 1}
  else if (precision == "8d"){ pattern = "(.*).*" ; ncolon = 3}
  else return('STOP')
  
  #get consensus/sample names/IDs
  samples=row.names(bwakit)
  # sort and filter reference according to results
  xref <<- ref[match(samples, rownames(ref)), 1:6]
  
  for (x in c("xref", typer)){
    assign(x, apply(get(x), c(1,2), fit_allele_to_precision, pattern, ncolon)) #cellwise trimming of type to wanted precision
    write.table(paste(precision,x,sep="."), x = get(x))
  }
  
  # for manual inspection and comparisons
  all_alleles = xref
  for (x in typer){
    all_alleles = cbind(all_alleles, get(x))
  }
  
  #build matrix
  acc = matrix(0, nrow=length(samples), ncol = length(typer)+1)
  rownames(acc) = samples
  colnames(acc) = c(typer, "possible hits")
  acc[, ncol(acc)] = apply(xref, 1, function(x) sum(x != "nottyped"))
  
  typercount = 0
  for (x in typer){
    hits = rep(0, length(samples))
    for (a in c(1,3,5)){ # diploid organisms are fun...
      pred = get(x)
      hits = hits + sapply(1:nrow(xref), function(i) compare_allele_pairs(pred[i,a:(a+1)], xref[i,a:(a+1)]))
    }
    typercount = typercount + 1
    acc[ ,typercount] = hits
  }
  return(list("accordance" = acc, "all_alleles" = all_alleles))
}

load_results()
acc = build_performance_table(precision='4d')
accordance =  acc[[1]]
all_alleles = acc[[2]]