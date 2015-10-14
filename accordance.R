build_ref_table <- function(){
# To generate the ref table
  ref <- read.csv("/vol/cs02/scratch/cmessers/projects/BIH/HLA/metadata/nar-02838-met-k-2014-File005.csv", header=FALSE)
  ref = head(ref, -2) #remove last 2 lines! Rubbish in there.
  rownames(ref) = make.names(ref[, 1], unique = T)
  colnames(ref) = make.names(ref[2, ], unique = T)
  ref = ref[3:nrow(ref), grep(pattern = ".*reference", ref[2, ])]
  write.table(ref, file = "ref.csv",quote = F, col.names = F)
}

# load all result files
load_results <- function(){
  #build_ref_table()
  ref <<- read.table("ref.csv", quote="\"", row.names=1)#[-c(3,7,13),]
  for (i in typer){
    assign(i, read.table(i, quote="\"", row.names=1)[1:6], envir = .GlobalEnv)
  }
}

find_consensus <- function(){
  #ref = ref[which(rownames(ref) %in% names(keepers2)),]
  samples <<- rownames(ref)
    
  for (i in typer){
    samples <<- intersect(samples, rownames(get(i)))    
  }
  samples <<- sort(samples)
  
  # sort and filter according to results
  xref <<- ref[match(samples, rownames(ref)),1:6]
  for (i in typer){
    assign(i, get(i)[match(samples, rownames(get(i))), 1:6], envir = .GlobalEnv)
  }
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

build_performance_table <- function(typer, precision){
  if      (precision == "2d"){ pattern = "(^[ABC]\\*[0-9]{2}).*" ; ncolon = 0}
  else if (precision == "4d"){ pattern = "(^[ABC]\\*[0-9]{2}:[0-9]{2,3}).*" ; ncolon = 1}
  else if (precision == "8d"){ pattern = "(.*).*" ; ncolon = 3}
  else return('STOP')
    
  load_results()
  find_consensus()

  for (x in c("xref", typer)){
    assign(x, apply(get(x), c(1,2), fit_allele_to_precision, pattern, ncolon)) #cellwise trimming of type to wanted precision
    write.table(paste(precision,x,sep="."), x = get(x), quote = F, col.names = F)
  }
  
  # for manual inspection and comparisons
  all_alleles = xref
  for (x in typer){
    all_alleles = cbind(all_alleles, get(x))
  }
  
  #build matrix
  acc = matrix(0, nrow=length(samples), ncol = length(typer)+1)
  rownames(acc) = samples
  colnames(acc) = c(typer, "alleles typed in ref")
  acc[, ncol(acc)] = apply(xref, 1, function(x) sum(x != "nottyped"))
  
  nnt = matrix(0, nrow=length(samples), ncol = length(typer))
  rownames(nnt) = samples
  colnames(nnt) = typer
                  
  typercount = 0
  for (x in typer){
    hits = rep(0, length(samples))
    nopred = rep(0, length(samples))
    
    #for (a in 1){
    for (a in c(1,3,5)){ # diploid organisms are fun...
      pred = get(x)
      hits   = hits   + sapply(1:nrow(xref), function(i) compare_allele_pairs(pred[i,a:(a+1)], xref[i,a:(a+1)]))
      nopred = nopred + sapply(1:nrow(pred), function(i) sum(pred[i,a:(a+1)] == "nottyped")) #count the number of untyped alleles to compute false positives later
    } 
    typercount = typercount + 1
    acc[ ,typercount] = hits
    nnt[ ,typercount] = nopred
  }
  return(list("accordance" = acc, "nnopred" = nnt, "all_alleles" = all_alleles))
}

compute_performance <- function(hittable, nopred){
  p = matrix(rep(hittable[,length(typer)+1], length(typer)), ncol=length(typer))
  
  fp = p - hittable[,1:length(typer)] - nopred
  # recall
  tpr = colSums(hittable[,1:length(typer)]) / colSums(p)
    
  fdr = colSums(fp)/(colSums(fp) + colSums(hittable[,1:length(typer)]))
  #precision
  ppv = 1 - fdr
  
  f_micro = (2*tpr*ppv)/(tpr+ppv)
  
  table = (cbind("Recall"=tpr,"Precision"=ppv, "Misclassification rate"=fdr, "F_micro measure"=f_micro))
  return(table)
}

options(stringsAsFactors = FALSE)
library(stringr)
precision='4d'
typer = c()
for (x in c("optitype", "bwakit", "hlassign", "phlat")){
  if (file.exists(x) &&  file.info(x)$size != 0 ) typer = append(typer, x)
}

acc = build_performance_table(typer, precision)
accordance =  acc[[1]]
nopred     =  acc[[2]]
#all_alleles = acc[[3]]

performance = compute_performance(accordance, nopred)
View(performance)
